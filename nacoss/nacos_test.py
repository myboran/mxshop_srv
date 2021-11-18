import nacos

SERVER_ADDERSSES = "server addresses split by comma"  # nacos "ip:port"
NAMESPACE = "***"  # namespace的id

# no auth mode
client = nacos.NacosClient(SERVER_ADDERSSES, namespace=NAMESPACE)
# auth mode
# client = nacos.NacosClient(SERVER_ADDRESSES, namespace=NAMESPACE, username="nacos", password="nacos")

# get config
data_id = "config.nacos"
group = "group"
print(client.get_config(data_id, group))
