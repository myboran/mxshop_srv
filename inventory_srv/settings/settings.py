import json
import redis
import nacos
from loguru import logger
from playhouse.pool import PooledMySQLDatabase
from playhouse.shortcuts import ReconnectMixin


# 使用连接池，保持长链接
class ReconnectMysqlDatabase(ReconnectMixin, PooledMySQLDatabase):
    pass


NACOS = {
    "Host": "192.168.190.129",
    "Port": 8848,
    "NameSpace": "b315663b-b3c1-494a-a7f4-a7d1cab3c8ef",
    "User": "nacos",
    "Password": "nacos",
    "DataId": "inventory.json",
    "Group": "dev"
}

client = nacos.NacosClient(f'{NACOS["Host"]}:{NACOS["Port"]}', namespace=NACOS["NameSpace"], username=NACOS["User"],
                           password=NACOS["Password"])
data = json.loads(client.get_config(NACOS["DataId"], NACOS["Group"]))

logger.info(data)

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

REDIS_HOST = data["redis"]["host"]
REDIS_PORT = data["redis"]["port"]
REDIS_DB = data["redis"]["db"]

# 配置一个连接池
pool = redis.ConnectionPool(host=REDIS_HOST, port=REDIS_PORT, db=REDIS_DB)
REDIS_CLIENT = redis.StrictRedis(connection_pool=pool)
