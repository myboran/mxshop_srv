import requests

headers = {
    "contentType": "application/json"
}


def register(name, id, address, port):
    url = "http://192.168.190.129:8500/v1/agent/service/register"

    rsp = requests.put(url, headers=headers, json={
        "Name": name,
        "ID": id,
        "Tags": ["mxshop", "bobby", "imocc", "web"],
        "Address": address,
        "Port": port,
        "Check": {
            "HTTP": f"http://{address}:{port}/health",
            "Timeout": "5s",
            "Interval": "5s",
            "DeregisterCriticalServiceAfter": "5s",
        }
    })
    if rsp.status_code == 200:
        print("注册成功")
    else:
        print(f"注册失败:{rsp.status_code}")


def deregister(id):
    url = f"http://192.168.190.129:8500/v1/agent/service/deregister/{id}"
    rsp = requests.put(url, headers=headers)
    if rsp.status_code == 200:
        print("注销成功")
    else:
        print(f"注销失败:{rsp.status_code}")


if __name__ == '__main__':
    register("mxshop-web", "mxshop-web", "192.168.230.1", 8021)
    # deregister("mxshop-web")
    pass
