# coding=utf-8


import struct
import logging

from tornado import ioloop, gen
from tornado.tcpclient import TCPClient


"""
tcpclient-struct.pack()组包
发送数据包格式:消息头+消息体
消息头:消息发送者(4字节)+消息接收者(4字节)+消息类型(1字节)+消息体中数据长度(4字节)
消息体:待发送数据

struct.unpack()拆包
接收数据包格式:消息头+消息体
消息头:消息发送者(4字节)+消息类型(1字节)+消息体中数据长度(4字节)
消息体:待接收数据
"""


logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)


class ChatClient(object):
    def __init__(self, host, port):
        self.host = host
        self.port = port

    @gen.coroutine
    def start(self):
        self.stream = yield TCPClient().connect(self.host, self.port)
        while True:
            yield self.send_message()
            yield self.receive_message()

    @gen.coroutine
    def send_message(self):
        # 待发送数据
        msg = input("输入:")
        bytes_msg = bytes(msg.encode("utf-8"))
        # 消息发送者
        chat_id = 10000000
        # 消息接收者
        receive_id = 10000001
        # 消息类型 1-文本 2-图片 3-语音 4-视频 等
        msg_type = 1

        binary_msg = struct.pack("!IIBI"+str(len(msg))+"s", chat_id, receive_id, msg_type, len(msg), bytes_msg)
        # 发送数据
        yield self.stream.write(binary_msg)

    @gen.coroutine
    def receive_message(self):
        """
        接收数据
        :return:
        """
        try:
            logger.debug("receive data ...")
            # 消息发送者 4字节
            sender = yield self.stream.read_bytes(4, partial=True)
            sender = struct.unpack('!I', sender)[0]
            logger.debug("sender:%s", sender)

            # 消息类型 1字节
            msg_type = yield self.stream.read_bytes(1, partial=True)
            msg_type = struct.unpack('!B', msg_type)[0]
            logger.debug("msg_type:%s", msg_type)

            # 消息长度 4字节
            msg_len = yield self.stream.read_bytes(4, partial=True)
            msg_len = struct.unpack('!I', msg_len)[0]
            logger.debug("msg_len:%s", msg_len)

            # 真实数据
            data = yield self.stream.read_bytes(msg_len, partial=True)
            data = struct.unpack("!" + str(msg_len) + "s", data)
            logger.debug("data:%s", data)
        except Exception as e:
            logger.error("tcp client exception:%s", e)


def main():
    c1 = ChatClient("127.0.0.1", 8888)
    c1.start()
    ioloop.IOLoop.instance().start()


if __name__ == '__main__':
    main()
