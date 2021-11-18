import socket
import sys
from concurrent import futures
import signal
import argparse
import os

import grpc
from loguru import logger


BASE_DIR = os.path.dirname(os.path.abspath(os.path.dirname(__file__)))
sys.path.insert(0, BASE_DIR)
from user_srv.settings.settings import client


from user_srv.proto import user_pb2_grpc
from user_srv.handler.user import UserServicer

from common.grpc_health.v1 import health, health_pb2_grpc
from common.register import consul
from user_srv.settings import settings


def on_exit(signo, frame):
    logger.info("进程中端")
    sys.exit(0)


def get_free_tcp_port():
    tcp = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    tcp.bind(("", 0))
    _, port = tcp.getsockname()
    tcp.close()

    return port


def serve():
    parse = argparse.ArgumentParser()
    parse.add_argument("--ip",
                       nargs="?",
                       type=str,
                       default="192.168.230.1",
                       help="binding ip"
                       )
    parse.add_argument("--port",
                       nargs="?",
                       type=int,
                       default=0,
                       help="the listening port"
                       )
    args = parse.parse_args()
    if args.port == 0:
        args.port = get_free_tcp_port()

    # logger.add("logs/user_srv_{time}.log")
    server = grpc.server(futures.ThreadPoolExecutor(max_workers=10))

    # 注册用户服务
    user_pb2_grpc.add_UserServicer_to_server(UserServicer(), server)
    # 注册健康检查
    health_pb2_grpc.add_HealthServicer_to_server(health.HealthServicer(), server)

    server.add_insecure_port(f"{args.ip}:{(args.port)}")
    server.start()
    logger.info(f"启动服务: {args.ip}:{args.port}]")

    #    SIGINT ctrl+C
    #    SIGTERM kill 发出的终止

    signal.signal(signal.SIGINT, on_exit)
    signal.signal(signal.SIGTERM, on_exit)

    logger.info(f"服务注册开始")
    register = consul.ConsulRegister(settings.CONSUL_HOST, settings.CONSUL_PORT)
    if not register.register(name=settings.SERVICE_NAME, id=settings.SERVICE_ID, address=args.ip, port=args.port,
                             tags=settings.SERVICE_TAGS, check=None):
        logger.info(f"服务注册失败")
        sys.exit(0)
    logger.info(f"服务注册成功")

    server.wait_for_termination()


def test_cb(args):
    print("配置文件产生变化")
    print(args)


if __name__ == '__main__':
    # logger.debug("调试信息")
    # logger.info("普通信息")
    # logger.warning("警告信息")
    # logger.error("错误信息")
    # logger.critical("严重错误信息")
    # logging.basicConfig()
    # print(get_free_tcp_port())
    client.add_config_watcher(settings.NACOS["DataId"], settings.NACOS["Group"], test_cb)
    serve()
