from __future__ import print_function, unicode_literals, division, absolute_import

import collections
import functools
import queue
import socket
import atexit
import sys


from control_and_bridge import *

_all_sockets = []
"""
V1.0 先完成一个客户端和服务器之间可以互相沟通的程序
    多个客户端可以同时连接到服务器上，每个客户端发送的数据在服务器端都能看到，服务器端发送的数据所有的客户端都能收到。
    则select中需要将sys.stdin加入，如果有键盘输入，就向所有的客户端发送输入的数据，
    如果有客户端连接进来，就把他加入到slave_pool中，
    如果有客户端发送过来的数据，就把他在服务器上打印显示
V2.0 可以让多个客户端之间通过服务器互相交流
"""


def split_host(x):
    """ "host:port" --> (host, int(port))"""
    try:
        host, port = x.split(":")
        port = int(port)
    except:
        raise ValueError(
            "wrong syntax, format host:port is "
            "required, not {}".format(x))
    else:
        return host, port


def fmt_addr(socket):
    """(host, int(port)) --> "host:port" """
    return "{}:{}".format(*socket)


def configure_logging(level):
    logging.basicConfig(
        level=level,
        format='[%(levelname)s %(asctime)s] %(message)s',
    )


log = logging.getLogger(__name__)
SPARE_SLAVER_TTL = 300


def try_close_sock(sock):
    """
    :type sock:socket.socket
    :param sock: 尝试关闭的socket
    :return:
    """
    try:
        sock.close()
    except:
        pass


def try_bind(sock, addr):
    """
    :type sock:socket.socket
    :type addr:tuple
    :return:None
    """
    while True:
        try:
            sock.bind(addr)
        except Exception as e:
            time.sleep(3)
        else:
            break


@atexit.register
def clean_after_close():
    log.info("existing....")
    for s in _all_sockets:
        try_close_sock(s)


class Master(object):
    def __init__(self, customer_listen_addr=("0.0.0.0", 10000), server_addr=("0.0.0.0", 9999)):
        # 服务器监听的地址
        # self.server_addr = server_addr
        self.ssl_context = False
        self.ssl_avail = False
        self.communicate_addr = server_addr
        # 线程池
        self.thread_pool = {"spare_slaver": {}, "working_slaver": {}}
        # 记录连接到服务器的socket
        self.slaver_pool = collections.deque()
        self.socket_bridge = SocketBridge()
        self.working_pool = {}
        self.customer_listen_addr = customer_listen_addr
        self.pending_customers = queue.Queue()
        self.thread_pool["listen_slaver"] = threading.Thread(
            target=self.listen_slave,
            name="listen_slaver-{}".format(self.communicate_addr),
            daemon=True
        )
        self.input = [sys.stdin, ]
        # self.thread_pool["read_and_write"] = threading.Thread(
        #     target=self.read_and_write,
        #     name="process read and write",
        #     daemon=True
        # )
        _fmt_communicate_addr = fmt_addr(self.communicate_addr)
        self.thread_pool["heart_beat_daemon"] = threading.Thread(
            target=self.heart_beat_daemon,
            name="heart_beat_daemon",
            daemon=True,
        )
        self.thread_pool["assign_slaver_daemon"] = threading.Thread(
            target=self._assign_slaver_daemon,
            name="assign_slaver_daemon-{}".format(_fmt_communicate_addr),
            daemon=True,
        )
        self.thread_pool["listen_customer"] = threading.Thread(
            target=self.listen_customer,
            name="listen_customer-{}".format(_fmt_communicate_addr),
            daemon=True,
        )

    def listen_customer(self):
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try_bind(sock, self.customer_listen_addr)
        sock.listen(20)
        _all_sockets.append(sock)
        log.info("Listening for customers: {}".format(
            fmt_addr(self.customer_listen_addr)))
        while True:
            conn_customer, addr_customer = sock.accept()
            log.info("Serving customer: {} Total customers: {}".format(
                addr_customer, self.pending_customers.qsize() + 1
            ))
            self.pending_customers.put((conn_customer, addr_customer))

    def _assign_slaver_daemon(self):
        while True:
            # 如果没有会阻塞
            conn_customer, addr_customer = self.pending_customers.get()
            try:
                conn_slaver = self.get_and_active_slaver()
            except:
                log.error('error in getting slaver', exc_info=True)
                continue
            if conn_slaver is None:
                log.warning("Closing customer[%s] because no available slaver found", addr_customer)
                try_close_sock(conn_customer)
                continue

            else:
                log.debug("Using slaver: %s for %s", conn_slaver.getpeername(), addr_customer)

            self.working_pool[addr_customer] = {
                "addr_customer": addr_customer,
                "conn_customer": conn_customer,
                "conn_slaver": conn_slaver,
            }

            try:
                self.server_customer(conn_customer, conn_slaver)
            except:
                log.error('error adding to socket_bridge', exc_info=True)
                try_close_sock(conn_customer)
                try_close_sock(conn_slaver)
                continue

    def serve_forever(self):
        self.thread_pool["listen_slaver"].start()
        # self.thread_pool["read_and_write"].start()
        self.thread_pool["heart_beat_daemon"].start()
        self.thread_pool["listen_customer"].start()
        self.thread_pool["assign_slaver_daemon"].start()
        self.thread_pool["socket_bridge"] = self.socket_bridge.start_as_daemon()

        while True:
            time.sleep(10)

    # 用来监听,将监听新的slaver的工作放到另一个线程中，这样在通信时就不用考虑这种情况，只需考虑输入和socket收到信息。
    def listen_slave(self):
        log.info("waiting for connect...")
        sock = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        try_bind(sock, self.communicate_addr)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        sock.listen(10)
        _all_sockets.append(sock)
        while True:
            conn, addr = sock.accept()
            self.slaver_pool.append({
                "addr_slaver": addr,
                "conn_slaver": conn
            })
            self.input.append(conn)
            log.info("get connect from {},total {}".format(addr, len(self.slaver_pool)))

    # 用来实现读取和写入数据
    def read_and_write(self):
        while True:
            if len(self.input) == 1:
                log.info("without connect...waiting for connect")
                time.sleep(2)
                continue
            read, write, _ = select.select(self.input, self.slaver_pool, [])
            for r in read:  # type:socket.socket
                # 如果是键盘的输入
                if r is sys.stdin:
                    # 将键盘输入的数据发送出去
                    data = bytes(input(">>:"))
                    # 多线程发送数据
                    send_thread = threading.Thread(
                        target=self.send_data,
                        name="send_data_to_all",
                        daemon=True,
                        args=(data),
                    )
                    send_thread.start()
                # 如果是客户端发来的数据
                else:
                    data = r.recv(100000)
                    if not data:
                        try_close_sock(r)
                        self.slaver_pool.remove(r)
                        self.input.remove(r)
                    log.info("message from {} and message is \n{}".format(r.getsockname(), repr(data)))

    def heart_beat_daemon(self):
        default_delay = 5 + SPARE_SLAVER_TTL // 12
        delay = default_delay
        log.info("heart beat daemon start delay : {}s".format(delay))
        while True:
            time.sleep(delay)  # 每次都睡眠一段时间，以此来减轻cpu负担
            slaver_count = len(self.slaver_pool)
            if not slaver_count:
                log.warning("heart_beat_daemon: sorry, no slaver available, keep sleeping")
                # restore default delay if there is no slaver
                delay = default_delay
                continue
            else:
                # 这样是为了保证delay尽可能的小，从而保证每个slaver都能在ttl之内进行报活
                delay = 1 + SPARE_SLAVER_TTL // max(slaver_count * 2 + 1, 12)
            slaver = self.slaver_pool.popleft()
            addr_slaver = slaver["addr_slaver"]

            start_time = time.perf_counter()
            try:
                hb_result = self.send_heartbeat(slaver["conn_slaver"])
            except Exception as e:
                log.warning("error during heartbeat to {}: {}".format(
                    fmt_addr(addr_slaver), e))
                log.debug(traceback.format_exc())
                hb_result = False
            finally:
                time_used = round((time.perf_counter() - start_time) * 1000.0, 2)

            # 如果心跳失败
            if not hb_result:
                log.warning("heart beat failed: {}, time: {}ms".format(
                    fmt_addr(addr_slaver), time_used))
                try_close_sock(slaver["conn_slaver"])
                del slaver["conn_slaver"]
                delay = 0
            else:
                log.debug("heartbeat success: {}, time: {}ms".format(
                    fmt_addr(addr_slaver), time_used))
                self.slaver_pool.append(slaver)

    def send_data(self, data):
        """
        :type data:str
        :param data:
        :return:
        """
        for conn, addr in self.slaver_pool:
            conn.send(data)
            log.info("send_data_to{}".format(addr))

    def send_heartbeat(self, conn):
        """
        发送心跳包
        :param conn: slaver的连接
        :type conn:socket.socket
        :return:
        """
        conn.send(CtrlPkg.pbuild_heart_beat().raw)  # 发送心跳包
        pkg, verify = CtrlPkg.recv(conn, except_type=CtrlPkg.PTYPE_HEART_BEAT)  # type:CtrlPkg,bool
        if not verify:
            return False
        conn.send(CtrlPkg.pbuild_heart_beat().raw)
        return verify

    def get_and_active_slaver(self):
        try_count = 100
        while True:
            try:
                dict_slaver = self.slaver_pool.popleft()
            except:
                if try_count:
                    time.sleep(0.02)
                    try_count -= 1
                    if try_count % 10 == 0:
                        log.error("!!NO SLAVER AVAILABLE!!  trying {}".format(try_count))
                    continue
                return None
            conn_slaver = dict_slaver["conn_slaver"]

            try:
                actual_conn = self.handshake(conn_slaver)
            except Exception as e:
                log.warning("Handshake failed. %s %s", dict_slaver["addr_slaver"], e)
                log.debug(traceback.format_exc())
                actual_conn = None

            if actual_conn is not None:
                return actual_conn
            else:
                log.warning("slaver handshake failed: %s", dict_slaver["addr_slaver"])
                try_close_sock(conn_slaver)

                time.sleep(0.02)

    def handshake(self, conn_slaver):
        """
        handshake before real data transfer
        it ensures:
            1. client is alive and ready for transmission
            2. client is shootback_slaver, not mistakenly connected other program
            3. verify the SECRET_KEY, establish SSL
            4. tell slaver it's time to connect target

        handshake procedure:
            1. master hello --> slaver
            2. slaver verify master's hello
            3. slaver hello --> master
            4. (immediately after 3) slaver connect to target
            4. master verify slaver
            5. [optional] establish SSL
            6. enter real data transfer

        Args:
            conn_slaver (socket.socket)
        Return:
            socket.socket|ssl.SSLSocket: socket obj(may be ssl-socket) if handshake success, else None
        """
        conn_slaver.send(CtrlPkg.pbuild_hs_m2s(ssl_avail=self.ssl_avail).raw)

        buff = select_recv(conn_slaver, CtrlPkg.PACKAGE_SIZE, 2)
        if buff is None:
            return None

        pkg, correct = CtrlPkg.decode_verify(buff, CtrlPkg.PTYPE_HS_S2M)  # type: CtrlPkg,bool

        if not correct:
            return None
        # 不起用ssl加密
        if not self.ssl_avail or pkg.data[1] == CtrlPkg.SSL_FLAG_NONE:
            if self.ssl_avail:
                log.warning('client %s not enabled SSL, fallback to plain.', conn_slaver.getpeername())
            return conn_slaver
        else:
            # 启用加密
            ssl_conn_slaver = self.ssl_context.wrap_socket(conn_slaver, server_side=True)  # type: ssl.SSLSocket
            log.debug('ssl established slaver: %s', ssl_conn_slaver.getpeername())
            return ssl_conn_slaver

    def trans_complete(self, addr_customer):
        """a callback for SocketBridge, do some cleanup jobs"""
        log.info("customer complete: {}".format(addr_customer))
        del self.working_pool[addr_customer]

    def server_customer(self, conn_customer: socket.socket, conn_slaver):
        self.socket_bridge.add_conn_pair(
            conn_customer, conn_slaver,
            functools.partial(
                self.trans_complete,
                conn_customer.getpeername()
            )
        )


def argparse_master():
    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.RawDescriptionHelpFormatter
    )
    parser.add_argument("-m", "--master", required=False,
                        metavar="host:port",
                        help="listening for slavers, usually an Public-Internet-IP. Slaver comes in here  eg: "
                             "2.3.3.3:10000")
    parser.add_argument("-c", "--customer", required=False,
                        metavar="host:port",
                        help="listening for customers, 3rd party program connects here  eg: 10.1.2.3:10022")
    # parser.add_argument("-k", "--secretkey", default="shootback",
    #                     help="secretkey to identity master and slaver, should be set to the same value in both side")
    # parser.add_argument("-v", "--verbose", action="count", default=0,
    #                     help="verbose output")
    # parser.add_argument("-q", "--quiet", action="count", default=0,
    #                     help="quiet output, only display warning and errors, use two to disable output")
    # parser.add_argument("-V", "--version", action="version", version="shootback {}-master".format(version_info()))
    # parser.add_argument("--ttl", default=300, type=int, dest="SPARE_SLAVER_TTL",
    #                     help="standing-by slaver's TTL, default is 300. "
    #                          "In master side, this value affects heart-beat frequency. "
    #                          "Default value is optimized for most cases")
    # parser.add_argument('--ssl', action='store_true', help='[experimental] try using ssl for data encryption. '
    #                                                        'It may be enabled by default in future version')

    return parser.parse_args()


def run_master(communicate_addr, customer_listen_addr, ssl=False):
    log.info("slaver from: {} customer from: {}".format(
        fmt_addr(communicate_addr), fmt_addr(customer_listen_addr)))

    Master(customer_listen_addr, communicate_addr).serve_forever()


def main_master():
    args = argparse_master()
    communicate_addr = split_host(args.master)
    customer_listen_addr = split_host(args.customer)
    CtrlPkg.recalc_crc32()
    configure_logging(logging.DEBUG)
    run_master(communicate_addr, customer_listen_addr)


if __name__ == '__main__':
    main_master()
