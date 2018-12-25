import binascii
import socket
import struct
import logging
import threading
import time
import traceback
import warnings

log = logging.getLogger(__name__)
try:
    import selectors
    from selectors import EVENT_READ, EVENT_WRITE

    EVENT_READ_WRITE = EVENT_READ | EVENT_WRITE
except ImportError:
    import select

    warnings.warn('selectors module not available, fallback to select')
    selectors = None

try:
    import ssl
except ImportError:
    ssl = None
    warnings.warn('ssl module not available, ssl feature is disabled')
"""
V1.0：对于内网穿透程序，需要master维持slaver的存活，所以需要心跳包，另外，在每次进行数据传输的时候，需要进行握手，来检测slaver和master的状态，
如果状态好，那么就进行传输，如果
则一共需要三种包的类型，心跳包：heartBeat,Master->Slaver,Slaver->Master
其中，心跳包中只包含包的类型以及一些控制信息，并不包含数据
而在M->S和S->M的包中，不仅包含控制信息，以及包的类型，也包含一些用来校验的数据，用来保证数据的传输不会出现错误，防止别人抓包进行诱骗
V2.0：在包中加上目标地址的控制信息，使服务器可以根据目标地址进行转发
"""
SECRET_KEY = "shootback"

INTERNAL_VERSION = 0x0011
RECV_BUFFER_SIZE = 2 ** 14


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


def select_recv(conn, buff_size, timeout=None):
    """
    add timeout for socket.recv()
    :type conn:socket.socket
    :return:收到的数据
    :rtype:Union[bytes,None]
    """
    if selectors:
        sel = selectors.DefaultSelector()
        sel.register(conn, EVENT_READ)
        events = sel.select(timeout)
        sel.close()
        if not events:
            raise RuntimeError("recv tiomeout")
    else:
        rlist, _, _ = select.select([conn], [], [], timeout)
    buff = conn.recv(buff_size)
    if not buff:
        raise RuntimeError("received zero bytes, socket was closed")
    return buff


class SocketBridge(object):
    def __init__(self):
        # 数据的交换发生在两个场景，一个是slaver与cust之间，另一个是slaver和自身的targer之间
        self.conn_rd = set()  # 放的是数据的接收方
        self.conn_wd = set()  # 放的是数据的发送方，
        self.map = {}  # 记录slaver和cust之间的映射关系，一一对应
        self.callbacks = {}  # 回调函数
        self.send_buff = {}  # 将读到的数据缓存起来

        if selectors:
            self.sel = selectors.DefaultSelector()
        else:
            self.sel = None

    def add_conn_pair(self, conn1: socket.socket, conn2: socket.socket, callback=None):
        conn1.setblocking(False)
        conn2.setblocking(False)

        # 将一对socket分别加入到读写队列中，因为数据可能从任意一个socket发送
        self.conn_rd.add(conn1)
        self.conn_wd.add(conn1)
        self.conn_rd.add(conn2)
        self.conn_wd.add(conn2)

        # 记录两个socket之间的关系
        self.map[conn1] = conn2
        self.map[conn2] = conn1

        if callback is not None:
            self.callbacks[conn1] = callback

        # 给两个socket注册读和写事件的监听
        if self.sel:  # type:selectors.DefaultSelector
            self.sel.register(conn1, EVENT_READ_WRITE)
            self.sel.register(conn2, EVENT_READ_WRITE)

    def start_as_daemon(self) -> threading.Thread:
        t = threading.Thread(target=self.start)
        t.daemon = True
        t.start()
        log.info("SocketBridge daemon started")
        return t

    def start(self):
        while True:
            try:
                self._start()
            except:
                log.error("FATAL ERROR! SocketBridge failed {}".format(
                    traceback.format_exc()
                ))

    def _start(self):

        while True:
            # 如果当前没有socket对，就休眠一下，节省cpu的开销
            if not self.conn_rd and not self.conn_wd:
                time.sleep(0.06)
                continue

            if self.sel:  # type:selectors.DefaultSelector
                events = self.sel.select(0.5)
                # 选出所有的读就绪的socket
                sockers_rd = tuple(key.fileobj for key, mask in events if mask & EVENT_READ)
                # 选出所有写就徐的socket
                sockers_wd = tuple(key.fileobj for key, mask in events if mask & EVENT_WRITE)
            else:
                r, w, _ = select.select(self.conn_rd, self.conn_wd, [], 0.5)
                sockers_rd = tuple(r)
                sockers_wd = tuple(w)

                # 在数据交换发生的较少时，减小cpu的开销
            if not sockers_rd and not self.send_buff:
                time.sleep(0.01)

            for s in sockers_rd:  # type:socket.socket
                # 如果当前socket对应的socket有未发送的数据，就跳过这一个，防止buff爆掉
                if self.map[s] in self.send_buff:
                    continue

                try:
                    received = s.recv(RECV_BUFFER_SIZE)
                except Exception as e:
                    if ssl and isinstance(e, (ssl.SSLWantReadError, ssl.SSLWantWriteError)):
                        # log.warning('got %s, wait to read then', repr(e))
                        continue

                    # unable to read, in most cases, it's due to socket close
                    log.warning('error reading socket %s, %s closing', repr(e), s)
                    self._rd_shutdown(s)
                    continue
                if not received:
                    self._rd_shutdown(s)
                    continue
                else:
                    self.send_buff[self.map[s]] = received
            for s in sockers_wd:
                if s not in self.send_buff:
                    if self.map.get(s) not in self.conn_rd:
                        self._wr_shutdown(s)
                    continue

                # 取出要发送的数据
                data = self.send_buff.pop(s)
                try:
                    s.send(data)
                except Exception as e:
                    if ssl and isinstance(e, (ssl.SSLWantReadError, ssl.SSLWantWriteError)):
                        # log.warning('got %s, wait to write then', repr(e))
                        self.send_buff[s] = data  # write back for next write
                        continue
                    # unable to send, close connection
                    log.warning('error sending socket %s, %s closing', repr(e), s)
                    # 如果出错，将socket写状态关闭，然后将其对应的socket从写队列中删除，并且将其从所有队列中除去
                    self._wr_shutdown(s)
                    continue

    def _rd_shutdown(self, conn, once=False):
        """action when connection should be read-shutdown
                :type conn: socket.socket
                """
        if conn in self.conn_rd:
            self.conn_rd.remove(conn)
            if self.sel:
                self._sel_disable_event(conn, EVENT_READ)

        # if conn in self.send_buff:
        #     del self.send_buff[conn]

        try:
            # 关闭读的功能，不能使用read or recv等功能
            conn.shutdown(socket.SHUT_RD)
        except:
            pass
        # 默认是将当前socket对应的socket转换成读状态
        if not once and conn in self.map:  # use the `once` param to avoid infinite loop
            # if a socket is rd_shutdowned, then it's
            #   pair should be wr_shutdown.
            self._wr_shutdown(self.map[conn], True)
        # 如果当前socket和对应的socket都被读过了，说明这一次的数据交换已经结束，则应该关闭这两个socket
        if self.map.get(conn) not in self.conn_rd:
            # if both two connection pair was rd-shutdowned,
            #   this pair sockets are regarded to be completed
            #   so we gonna close them
            self._terminate(conn)

    def _sel_disable_event(self, conn, ev):
        try:
            _key = self.sel.get_key(conn)  # type:selectors.SelectorKey
        except KeyError:
            pass
        else:
            if _key.events == EVENT_READ_WRITE:
                # 转换监听的状态，如果当前是读，就变为写，如果是写，就变为读
                self.sel.modify(conn, EVENT_READ_WRITE ^ ev)
            else:
                self.sel.unregister(conn)

    def _wr_shutdown(self, conn, once=False):
        # 将写完的socket关闭
        """action when connection should be write-shutdown
        :type conn: socket.socket
        """
        try:
            # 关闭当前socket写的功能，不能使用send/write等
            conn.shutdown(socket.SHUT_WR)
        except:
            pass

        # 如果当前socket在连接的写列表中
        if conn in self.conn_wd:
            # 把他从列表中去除
            self.conn_wd.remove(conn)
            # 然后讲绑定到他的监听器取消
            if self.sel:
                self._sel_disable_event(conn, EVENT_WRITE)
        # 下面的if只有在当前的socket已经被处理完成后，主动调用这个函数，将他的对应的socket转换状态
        if not once and conn in self.map:  # use the `once` param to avoid infinite loop
            #   pair should be rd_shutdown.
            # if a socket is wr_shutdowned, then it's
            self._rd_shutdown(self.map[conn], True)

    def _terminate(self, conn, once=False):
        """terminate a sockets pair (two socket)
        :type conn: socket.socket
        :param conn: any one of the sockets pair
        """
        try_close_sock(conn)  # close the first socket

        # ------ close and clean the mapped socket, if exist ------
        _another_conn = self.map.pop(conn, None)

        self.send_buff.pop(conn, None)
        if self.sel:
            try:
                self.sel.unregister(conn)
            except:
                pass

        # ------ callback --------
        # because we are not sure which socket are assigned to callback,
        #   so we should try both
        if conn in self.callbacks:
            try:
                self.callbacks[conn]()
            except Exception as e:
                log.error("traceback error: {}".format(e))
                log.debug(traceback.format_exc())
            del self.callbacks[conn]

        # terminate another
        if not once and _another_conn in self.map:
            self._terminate(_another_conn)


class CtrlPkg(object):
    PACKAGE_SIZE = 2 ** 6  # 64bytes
    TIME_OUT = 5  # 接收时间的过期时间

    SECRET_KEY_CRC32 = binascii.crc32(SECRET_KEY.encode("utf-8")) & 0xffffffff
    SECRET_KEY_REVERSED_CRC32 = binascii.crc32(SECRET_KEY[::-1].encode('utf-8')) & 0xffffffff

    # 定义三中包的类型
    PTYPE_HS_S2M = -1
    PTYPE_HEART_BEAT = 0
    PTYPE_HS_M2S = +1

    TYPE_NAME_MAP = {
        PTYPE_HS_S2M: "PTYPE_HS_S2M",
        PTYPE_HEART_BEAT: "PTYPE_HEART_BEAT",
        PTYPE_HS_M2S: "PTYPE_HS_M2S",
    }
    '''
    定义二进制包的结构，integer 长度为1 integer 长度为1 integer 长度为2 20个保留长度 40个数据长度
    '''
    FORMAT_PKG = b"!b b H 20x 40s"
    FORMATS_DATA = {
        PTYPE_HS_S2M: b"!I B 35x",
        PTYPE_HEART_BEAT: b"!40x",
        PTYPE_HS_M2S: b"!I B 35x",
    }
    SSL_FLAG_NONE = 0
    SSL_FLAG_AVAIL = 1

    def __init__(self, pkg_ver=0x01, pkg_type=0,
                 prgm_ver=INTERNAL_VERSION, data=(),
                 raw=None, ):
        self.pkg_ver = pkg_ver
        self.pkg_type = pkg_type
        self.prgm_ver = prgm_ver
        self.data = data
        # raw应该是本次包的二进制版本，将所有信息打包成二进制用来在网络中进行传输
        if raw:
            self.raw = raw
        else:
            # 如果没有，就进行构建
            self._build_bytes()

    @property
    def type_name(self):
        return self.TYPE_NAME_MAP.get(self.pkg_type, "TypeUnknown")

    def __str__(self):
        return """pkg_ver: {} pkg_type:{} prgm_ver:{} data:{}""".format(
            self.pkg_ver,
            self.type_name,
            self.prgm_ver,
            self.data,
        )

    def __repr__(self):
        return self.__str__()

    def _build_bytes(self):
        """
        根据结构信息，将当前对象的信息构建成为二进制包，用于在网络中进行传输
        :return:
        """
        self.raw = struct.pack(
            self.FORMAT_PKG,
            self.pkg_ver,
            self.pkg_type,
            self.prgm_ver,
            self.data_encode(self.pkg_type, self.data)
        )

    @classmethod
    def recalc_crc32(cls):
        """
        重新计算加密密钥的crc32校验值,用来在Master和Slaver中发送数据时填充数据校验字段
        """
        cls.SECRET_KEY_CRC32 = binascii.crc32(SECRET_KEY.encode('utf-8')) & 0xffffffff
        cls.SECRET_KEY_REVERSED_CRC32 = binascii.crc32(SECRET_KEY[::-1].encode('utf-8')) & 0xffffffff

    @classmethod
    def data_encode(cls, ptype, data):
        """
        根据包的类型，构建包的数据部分
        :param ptype:包的类型，
        :param data: 数据
        :return: 返回构建完成的data部分bytes类型
        """
        return struct.pack(cls.FORMATS_DATA[ptype], *data)

    @classmethod
    def data_decode(cls, ptype, data_raw):
        """
        根据收到的包的类型进行解包
        :param ptype: 包的类型
        :param data_raw: 数据部分的二进制数据
        :return: 返回解包后的数据字段
        """
        return struct.unpack(cls.FORMATS_DATA[ptype], data_raw)

    def verify(self, except_pkg_type=None):
        """
        传入期望的包的类型，与当前收到的包的类型进行比对
        :param except_pkg_type: 期望收到的包的类型
        :return: 是否符合要求
        """
        try:
            # 如果收到的包类型不为空，且包的类型和期望的类型不一致，则返回False
            if except_pkg_type is not None and self.pkg_type != except_pkg_type:
                return False
            # 如果收到的包是由S->M的，则比对包的数据部分是否能够通过校验，用来防止别人偷包，检测网络的质量
            elif self.pkg_type == self.PTYPE_HS_S2M:
                # Slaver-->Master 的握手响应包
                return self.data[0] == self.SECRET_KEY_REVERSED_CRC32
            # 同上
            elif self.pkg_type == self.PTYPE_HS_M2S:
                # Master-->Slaver 的握手包
                return self.data[0] == self.SECRET_KEY_CRC32
            # 如果是心跳包，直接返回True
            elif self.pkg_type == self.PTYPE_HEART_BEAT:
                return True
            else:
                return True
        except:
            return False

    @classmethod
    def decode_only(cls, raw):
        """
        只把当前的二进制包解包，变成包的实例
        :param raw: 数据包的二进制内容
        :type raw bytes
        :return: 一个数据包对象
        """
        # 如果当前raw不存在，或者raw的长度不等于定义的数据包的长度，则表明包可能在传输途中损坏，或者是别人伪造的包，则应该丢弃并警告
        if not raw or len(raw) != cls.PACKAGE_SIZE:
            raise ValueError("content size should be {}, but {}".format(
                cls.PACKAGE_SIZE, len(raw)
            ))
        pkg_ver, pkg_type, prgm_ver, data_raw = struct.unpack(cls.FORMAT_PKG, raw)
        data = cls.data_decode(pkg_type, data_raw)
        return cls(
            pkg_ver=pkg_ver, pkg_type=pkg_type,
            prgm_ver=prgm_ver,
            data=data,
            raw=raw,
        )

    @classmethod
    def decode_verify(cls, raw, pkg_type=None):
        """
        对包进行解码，并且验证是否是符合要求类型的包
        :param raw: 包的二进制数据
        :param pkg_type: 期望的包的类型
        :rtype CtrlPkg,bool
        :return: 包的对象，以及是否是一个合法的包的元组
        """
        try:
            pkg = cls.decode_only(raw)
        except:
            log.error('unable to decode package. raw: %s', raw, exc_info=True)
            return None, False
        else:
            return pkg, pkg.verify(pkg_type)

    @classmethod
    def pbuild_hs_m2s(cls, ssl_avail=False):
        """
        构建从Master发往Slaver的数据包
        :param ssl_avail:
        :return: 数据包
        """
        ssl_flag = cls.SSL_FLAG_AVAIL if ssl_avail else cls.SSL_FLAG_NONE
        return cls(
            pkg_type=cls.PTYPE_HS_M2S,
            data=(cls.SECRET_KEY_CRC32, ssl_flag)
        )

    @classmethod
    def pbuild_hs_s2m(cls, ssl_avail=False):
        ssl_flag = cls.SSL_FLAG_AVAIL if ssl_avail else cls.SSL_FLAG_NONE
        return cls(
            pkg_type=cls.PTYPE_HS_S2M,
            data=(cls.SECRET_KEY_REVERSED_CRC32, ssl_flag),
        )

    @classmethod
    def pbuild_heart_beat(cls):
        return cls(
            pkg_type=cls.PTYPE_HEART_BEAT
        )

    @classmethod
    def recv(cls, sock, timeout=TIME_OUT, except_type=None):
        """
        接收数据包，并且校验这个包
        :param sock: 用来接受数据的socket
        :type sock:socket.socket
        :param timeout: 过期时间
        :param except_type: 期望收到的包的类型
        :return: 数据包和是否通过校验
        """
        buff = select_recv(sock, cls.PACKAGE_SIZE, timeout)
        pkg, verify = cls.decode_verify(buff, except_type)  # type:CtrlPkg,bool
        return pkg, verify
