import json

import nacos
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


# 使用连接池，保持长链接
class ReconnectMysqlDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


NACOS = {
    "Host": "192.168.190.132",
    "Port": 8848,
    "NameSpace": "1c0258f4-2572-461b-ba6b-06da9132e0c5",
    "User": "nacos",
    "Password": "nacos",
    "DataId": "goods-srv.json",
    "Group": "dev"
}

client = nacos.NacosClient(f'{NACOS["Host"]}:{NACOS["Port"]}', namespace=NACOS["NameSpace"], username=NACOS["User"],
                           password=NACOS["Password"])
data = json.loads(client.get_config(NACOS["DataId"], NACOS["Group"]))

MYSQLINFO = data["mysql"]
# 创建数据库
MYSQL_DB = MYSQLINFO["db"]
MYSQL_HOST = MYSQLINFO["host"]
MYSQL_PORT = MYSQLINFO["port"]
MYSQL_USER = MYSQLINFO["user"]
MYSQL_PASSWORD = MYSQLINFO["password"]
DB = ReconnectMysqlDatabase(database=MYSQL_DB, host=MYSQL_HOST, port=MYSQL_PORT, user=MYSQL_USER,
                            password=MYSQL_PASSWORD)

CONSULINFO = data["consul"]
# consul配置
CONSUL_HOST = CONSULINFO["host"]
CONSUL_PORT = CONSULINFO["port"]

import uuid

# 服务相关的配置
SERVICE_NAME = data["name"]
SERVICE_ID = str(uuid.uuid1())
SERVICE_TAGS = data["tags"]
