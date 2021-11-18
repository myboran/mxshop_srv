import time

import grpc

from user_srv.proto import user_pb2_grpc, user_pb2


class UserTest:
    def __init__(self):
        # 连接grpc服务器
        channel = grpc.insecure_channel("127.0.0.1:50051")
        self.stub = user_pb2_grpc.UserStub(channel)

    def user_list(self):
        rps: user_pb2.UserListResponse = self.stub.GetUserList(user_pb2.PageInfo(pn=2, pSize=3))
        print(rps.total)
        for user in rps.data:
            print(user.mobile, user.id)

    def get_user_by_id(self, id):
        rsp: user_pb2.UserInfoResponse = self.stub.GetUserById(user_pb2.IdRequest(id=id))
        print(rsp.mobile, rsp.id)

    def create_user(self, nick_name, mobile, password):
        rsp: user_pb2.CreateUserInfo = self.stub.CreateUser(
            user_pb2.CreateUserInfo(nickName=nick_name, passWord=password, mobile=mobile))
        print(rsp.mobile, rsp.id, rsp.nickName)


if __name__ == '__main__':
    user = UserTest()
    user.user_list()
    print("-------")
    # user.get_user_by_id(10)
    # print("-----------")
    # user.create_user(nick_name="myboran3", mobile="15628286923", password="ACB123456")
