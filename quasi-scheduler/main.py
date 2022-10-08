import requests
import time
import sys
import const
from kubernetes import config, client
from util import getScore
from model import NodeInfo, FaasFunc

CRITICAL_THRESHOLD = 50

config.load_kube_config()
v1 = client.CoreV1Api()

faas_functions = dict()
nodes_info = dict()

r0 = requests.get(url=const.url, params=const.query["total_memory"])
total_mem_json = r0.json()["data"]["result"]

for result in total_mem_json:
    node_name = result["metric"].get("node_name", "")
    # TODO Check this conversion
    total_memory = float(result["value"][1]) / 1024**3
    nodes_info[node_name] = NodeInfo(total_memory)


def identifyCriticalNodes(nodes_info):
    for key in nodes_info:
        score = getScore(
            nodes_info[key].get_current_mem_usage(),
            nodes_info[key].get_current_cpu_usage(),
        )
        nodes_info[key].set_score(score)
        if score >= CRITICAL_THRESHOLD:
            nodes_info[key].set_to_critical()
            reschedulingNeeded = True


global reschedulingNeeded
# Query every 15 seconds
while True:
    reschedulingNeeded = False
    nodes = []
    # functions = []
    row = 0

    r1 = requests.get(url=const.url, params=const.query["mem_usage"])
    r2 = requests.get(url=const.url, params=const.query["cpu_usage"])
    r3 = requests.get(
        url=const.url, params=const.query["function_invocation_per_minut"]
    )

    mem_json = r1.json()["data"]["result"]
    cpu_json = r2.json()["data"]["result"]
    functions_json = r3.json()["data"]["result"]

    for result in mem_json:
        node_name = result["metric"].get("node_name", "")
        mem = float(result["value"][1])
        nodes_info[node_name].set_current_mem_usage(mem)
        # TODO remove nodes, it is using for debugging
        nodes.append([node_name, mem])

    for result in cpu_json:
        node_name = result["metric"].get("node_name", "")
        cpu = float(result["value"][1])
        nodes_info[node_name].set_current_cpu_usage(cpu)
        # TODO remove nodes, it is using for debugging
        nodes[row].append(cpu)
        row = row + 1

    identifyCriticalNodes(nodes_info)
    if reschedulingNeeded:
        print("#####RESCHEDULING####")
        for result in functions_json:
            function_name = (
                result["metric"].get("function_name", "").split(const.delimetar)[0]
            )
            invocation = result["value"][1]
            faas_functions[function_name] = FaasFunc(invocation)
            # functions.append([function_name,invocation])
        # node_list=v1.list_node()
        # nasdame=node_list._items[0]._metadata.name
        pod_list = v1.list_namespaced_pod("openfaas-fn")
        for pod in pod_list.items:
            function_name = pod.metadata.labels["faas_function"]
            faas_functions[function_name].set_node(pod.spec.node_name)

    # TODO remove print, it is using for debugging
    print("instance | memory | cpu")
    for node in nodes:
        line = str(node[0]) + " | " + str(node[1]) + " | " + str(node[2])
        print(str(line))
    sys.stdout.flush()

    print("#######################")
    time.sleep(15)
