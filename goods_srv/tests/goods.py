import consul
import grpc

from goods_srv.proto import goods_pb2, goods_pb2_grpc
from goods_srv.settings import settings


class GoodsTest:

    def __init__(self):

        c = consul.Consul(host="192.168.190.129", port=8500)
        services = c.agent.services()

        ip = ""
        port = ""
        for key, value in services.items():
            if value["Service"] == settings.SERVICE_NAME:
                ip = value["Address"]
                port = value["Port"]
                break
        if not ip:
            raise Exception()
        channel = grpc.insecure_channel(f"{ip}:{port}")
        self.goods_stub = goods_pb2_grpc.GoodsStub(channel)

    def goods_list(self):
        rsp: goods_pb2.GoodsListResponse = self.goods_stub.GoodsList(
            goods_pb2.GoodsFilterRequest(keyWords="山")
        )
        for item in rsp.data:
            print(item.name, item.shopPrice)

    def get_detail(self, id):
        rsp = self.goods_stub.GetGoodsDetail(goods_pb2.GoodsInfoResponse(
            id=id
        ))
        print(rsp.name)


if __name__ == "__main__":
    goods = GoodsTest()

    goods.goods_list()
    goods.get_detail(2)
    pass
