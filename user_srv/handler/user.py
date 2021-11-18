import signal
import time
from datetime import date

import grpc
from google.protobuf import empty_pb2
from passlib.handlers.pbkdf2 import pbkdf2_sha256
from peewee import DoesNotExist

from user_srv.proto import user_pb2, user_pb2_grpc
from user_srv.model.models import User

from loguru import logger


class UserServicer(user_pb2_grpc.UserServicer):

    @logger.catch
    def convert_user_to_rsp(self, user):
        # 将user的model对象转换成message对象
        user_info_rsp = user_pb2.UserInfoResponse()

        user_info_rsp.id = user.id
        user_info_rsp.passWord = user.password
        user_info_rsp.mobile = user.mobile
        user_info_rsp.role = user.role

        if user.nick_name:
            user_info_rsp.nickName = user.nick_name
        if user.gender:
            user_info_rsp.gender = user.gender
        if user.birthday:
            user_info_rsp.birthDay = int(time.mktime(user.birthday.timetuple()))

        return user_info_rsp

    def GetUserList(self, request: user_pb2.PageInfo, context):
        # 获取列表用户
        logger.info("得到用户列表")
        rsp = user_pb2.UserListResponse()
        users = User.select()
        rsp.total = users.count()

        start = 0
        per_pag_nums = 10
        if request.pSize:
            per_pag_nums = request.pSize
        if request.pn:
            start = per_pag_nums * (request.pn - 1)
        users = users.limit(per_pag_nums).offset(start)

        for user in users:
            rsp.data.append(self.convert_user_to_rsp(user))
        return rsp

    def GetUserById(self, request, context):
        # 通过 id 查询用户
        try:
            user = User.get(User.id == request.id)
            return self.convert_user_to_rsp(user)

        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
            return user_pb2.UserInfoResponse()

    def GetUserByMobile(self, request, context):
        # 通过 mobile 查询用户
        try:
            user = User.get(User.mobile == request.mobile)
            return self.convert_user_to_rsp(user)

        except DoesNotExist as e:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
            return user_pb2.UserInfoResponse()

    def CreateUser(self, request, context):
        # 创建用户
        try:
            user = User.get(User.mobile == request.mobile)
            context.set_code(grpc.StatusCode.ALREADY_EXISTS)
            context.set_details("用户已存在")
            return user_pb2.UserInfoResponse()
        except DoesNotExist as e:
            pass

        user = User()
        user.nick_name = request.nickName
        user.mobile = request.mobile
        user.password = pbkdf2_sha256.hash(request.passWord)
        user.save()

        return self.convert_user_to_rsp(user)

    def UpdateUser(self, request, context):
        try:
            user = User.get(User.id == request.id)
            user.nick_name = request.nickName
            user.gender = request.gender
            user.birthday = date.fromtimestamp(request.birthDay)
            user.save()
            return empty_pb2.Empty()

        except DoesNotExist:
            context.set_code(grpc.StatusCode.NOT_FOUND)
            context.set_details("用户不存在")
            return user_pb2.UserInfoResponse()

    @logger.catch
    def CheckPassWord(self, request, context):
        return user_pb2.CheckResponse(success=pbkdf2_sha256.verify(request.password, request.encryptedPassword))
