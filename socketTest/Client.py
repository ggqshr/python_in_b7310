import functools
import socket
from Master import *


class Client(object):
    def __init__(self, server_addr=("0.0.0.0", 9999), targer_addr=("0.0.0.0", 22)):
        self.target_addr = targer_addr
        self.working_pool = {}
        self.max_spare_count = 1
        self.server_addr = server_addr
        self.spare_slaver_pool = {}
        self.input = [sys.stdin, ]
        self.ssl_avail = False
        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self.socket_bridge = SocketBridge()

    def process(self):
        log.info("connect to the master")
        try:
            self.sock.connect(self.server_addr)
        except:
            log.warn("can't connect to the Master")
            try_close_sock(self.sock)
        self.input.append(self.sock)
        while True:
            rr, ww, _ = select.select(self.input, [], [])
            for r in rr:  # type:socket.socket
                if r is sys.stdin:
                    data = input(">>:")
                    log.info("send {} to the master".format(data))
                    dd = bytes(data, encoding="utf8")
                    self.sock.sendall(dd)
                else:
                    data = r.recv(10000)
                    if not data:
                        self.input.remove(self.sock)
                        try_close_sock(self.sock)
                        self.sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
                        self.sock.connect(self.server_addr)
                        self.input.append(self.sock)
                        continue
                    log.info("the message from master is {}".format(repr(data)))

    def server_forever(self):
        err_delay = 0
        max_err_delay = 15
        spare_delay = 0.08
        default_spare_delay = 0.08
        self.socket_bridge.start_as_daemon()
        while True:
            if len(self.spare_slaver_pool) >= self.max_spare_count:
                time.sleep(spare_delay)
                spare_delay = (spare_delay + default_spare_delay) / 2.0
                continue
            else:
                spare_delay = 0.0

            try:
                conn = self.connect_master()
            except Exception as e:
                # 在发生错误的时候，会休眠一段时间，随着错误次数的增加，休眠的时间也会增加，以此来减少CPU占用率
                log.warning("unable to connect master {}".format(e), exc_info=True)
                time.sleep(err_delay)
                if err_delay < max_err_delay:
                    err_delay += 1
                continue

            try:
                t = threading.Thread(target=self.slaver_working, args=(conn,))
                t.daemon = True
                t.start()
                log.info("connected to master[{}] at {} total: {}".format(
                    fmt_addr(conn.getpeername()),
                    fmt_addr(conn.getsockname()),
                    len(self.spare_slaver_pool),
                ))
            except Exception as e:
                log.error("unable create Thread: {}".format(e))
                log.debug(traceback.format_exc())
                time.sleep(err_delay)

                if err_delay < max_err_delay:
                    err_delay += 1
                continue

            err_delay = 0

    def _transfer_complete(self, addr_slaver):
        """a callback for SocketBridge, do some cleanup jobs"""
        pair = self.working_pool.pop(addr_slaver)
        try_close_sock(pair['conn_slaver'])
        try_close_sock(pair['conn_target'])
        log.info("slaver complete: {}".format(addr_slaver))

    def stage_ctrlpkg(self, conn):
        while True:
            pkg, correct = CtrlPkg.recv(conn, SPARE_SLAVER_TTL)  # type: CtrlPkg,bool
            log.debug("{}".format(correct))
            if not correct:
                return None

            log.debug("CtrlPkg from {}: {}".format(conn.getpeername(), pkg))

            if pkg.pkg_type == CtrlPkg.PTYPE_HEART_BEAT:
                if not self.response_heartbeat(conn, pkg):
                    return None

            elif pkg.pkg_type == CtrlPkg.PTYPE_HS_M2S:
                break
        log.debug("begin to handshake...")
        actual_conn = self.response_handshake(conn, pkg)
        log.debug("end handshake...")

        return actual_conn

    def response_handshake(self, conn, handshake_pkg):
        """
        :type conn:socket.socket
        :type handshake_pkg:CtrlPkg
        :param conn:
        :param handshake_pkg:
        :return:
        """
        conn.send(CtrlPkg.pbuild_hs_s2m(ssl_avail=self.ssl_avail).raw)
        if not self.ssl_avail or handshake_pkg.data[1] == CtrlPkg.SSL_FLAG_NONE:
            log.debug("no ssl use plain socket to return ....")
            if self.ssl_avail:
                log.warning('master %s does not enabled SSL, fallback to plain', conn.getpeername())
            return conn
        else:
            ssl_conn_slaver = self.ssl_context.wrap_socket(conn, server_side=False)  # type: ssl.SSLSocket
            log.debug('ssl established slaver: %s', ssl_conn_slaver.getpeername())
            return ssl_conn_slaver

    def response_heartbeat(self, conn, pkg):
        """
        :type conn:socket.socket
        :param conn:
        :param pkg:
        :return:
        """
        conn.send(CtrlPkg.pbuild_heart_beat().raw)
        pkg, verify = CtrlPkg.recv(conn, except_type=CtrlPkg.PTYPE_HEART_BEAT)
        if verify:
            log.debug("heartbeat success {}".format(
                fmt_addr(conn.getsockname())))
            return True
        else:
            log.warning(
                "received a wrong pkg[{}] during heartbeat, {}".format(
                    pkg, conn.getsockname()
                ))
            return False

    def connect_master(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.server_addr)

        self.spare_slaver_pool[sock.getsockname()] = {"conn_slaver": sock}
        return sock

    def slaver_working(self, conn):
        """
        :type conn:socket.socket
        :param conn:
        :return:
        """
        # 获得当前地址
        addr_slaver = conn.getsockname()
        # 获得服务器地址
        addr_master = conn.getpeername()

        try:
            actual_conn = self.stage_ctrlpkg(conn)
        except Exception as e:
            log.warning("slaver{} waiting handshake failed {}".format(
                fmt_addr(addr_slaver), e))
            log.debug(traceback.print_exc())
            actual_conn = None
        else:
            if actual_conn is None:
                log.warning("bad handshake or timeout between: {} and {}".format(
                    fmt_addr(addr_master), fmt_addr(addr_slaver)))

        if actual_conn is None:
            del self.spare_slaver_pool[addr_slaver]
            try_close_sock(conn)

            log.warning("a slaver[{}] abort due to handshake error or timeout".format(
                fmt_addr(addr_slaver)))
            return
        else:
            log.info("Success master handshake from: {} to {}".format(
                fmt_addr(addr_master), fmt_addr(addr_slaver)))

        self.working_pool[addr_slaver] = self.spare_slaver_pool.pop(addr_slaver)
        self.working_pool[addr_slaver]['conn_slaver'] = actual_conn

        try:
            conn_target = self._connect_target()
        except:
            log.error("unable to connect target")
            try_close_sock(actual_conn)

            del self.working_pool[addr_slaver]
            return
        self.working_pool[addr_slaver]["conn_target"] = conn_target
        try:
            self.socket_bridge.add_conn_pair(
                actual_conn, conn_target,
                functools.partial(
                    # 这个回调用来在传输完成后删除工作池中对应记录
                    self._transfer_complete, addr_slaver
                )
            )
        except:
            log.error('error adding to socket_bridge', exc_info=True)
            try_close_sock(actual_conn)
            try_close_sock(conn_target)

        # this slaver thread exits here
        return

    def _connect_target(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        sock.connect(self.target_addr)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        log.debug("connected to target[{}] at: {}".format(
            sock.getpeername(),
            sock.getsockname(),
        ))

        return sock


def run_slaver(communicate_addr, target_addr):
    log.info("running as slaver, master addr: {} target: {}".format(
        fmt_addr(communicate_addr), fmt_addr(target_addr)
    ))

    Client(communicate_addr, target_addr,
           ).server_forever()


def argparse_slaver():
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-m", "--master", required=False,
                        metavar="host:port",
                        help="master address, usually an Public-IP. eg: 2.3.3.3:5500")
    parser.add_argument("-t", "--target", required=False,
                        metavar="host:port",
                        help="where the traffic from master should be tunneled to, usually not public. eg: 10.1.2.3:80")
    # parser.add_argument("-k", "--secretkey", default="shootback",
    #                     help="secretkey to identity master and slaver, should be set to the same value in both side")
    # parser.add_argument("-v", "--verbose", action="count", default=0,
    #                     help="verbose output")
    # parser.add_argument("-q", "--quiet", action="count", default=0,
    #                     help="quiet output, only display warning and errors, use two to disable output")
    # parser.add_argument("-V", "--version", action="version", version="shootback {}-slaver".format(version_info()))
    # parser.add_argument("--ttl", default=300, type=int, dest="SPARE_SLAVER_TTL",
    #                     help="standing-by slaver's TTL, default is 300. "
    #                          "this value is optimized for most cases")
    # parser.add_argument("--max-standby", default=5, type=int, dest="max_spare_count",
    #                     help="max standby slaver TCP connections count, default is 5. "
    #                          "which is enough for more than 800 concurrency. "
    #                          "while working connections are always unlimited")
    # parser.add_argument('--ssl', action='store_true', help='[experimental] try using ssl for data encryption. '
    #                                                        'It may be enabled by default in future version')

    return parser.parse_args()


def main_slaver():
    global SPARE_SLAVER_TTL
    global SECRET_KEY

    args = argparse_slaver()

    communicate_addr = split_host(args.master)
    target_addr = split_host(args.target)

    CtrlPkg.recalc_crc32()

    configure_logging(logging.DEBUG)
    log.info("Master: {}".format(fmt_addr(communicate_addr)))
    log.info("Target: {}".format(fmt_addr(target_addr)))

    # communicate_addr = ("localhost", 12345)
    # target_addr = ("93.184.216.34", 80)  # www.example.com

    run_slaver(communicate_addr, target_addr,
               )


if __name__ == '__main__':
    main_slaver()
