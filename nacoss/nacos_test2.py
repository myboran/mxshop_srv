import json
import time

import nacos

SERVER_ADDRESSES = "192.168.190.129:8848"  # nacos "ip:port"
NAMESPACE = "5c976fbc-ff24-4834-bdb6-fc51f9b265d1"  # namespace的id

# no auth mode
# client = nacos.NacosClient(SERVER_ADDERSSES, namespace=NAMESPACE)
# auth mode
client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, username="nacos", password="nacos")

# get config
data_id = "user-srv.json"
group = "dev"

rsp = json.loads(client.get_config(data_id, group))
print(rsp)


def test_cb(args):
    print("配置文件产生变化")
    print(args)


if __name__ == '__main__':
    client.add_config_watcher(data_id, group, test_cb)
    time.sleep(3000)
