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
api_v1 = client.AppsV1Api()

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
    global reschedulingNeeded
    score = 0
    for key in nodes_info:
        score = getScore(
            nodes_info[key].get_current_mem_usage(),
            nodes_info[key].get_current_cpu_usage(),
        )
        # for testing
        # if score == 0:
        #     score = 100
        # else:
        #     score = 10
        nodes_info[key].set_score(score)
        if score >= CRITICAL_THRESHOLD:
            nodes_info[key].set_to_critical()
            reschedulingNeeded = True


def rescheduleDeployment(api_v1, deployment, deployment_name, cnodes):
    print("Update selectedNode propertie")
    print(cnodes[0])
    # kubernetes.io/hostname=kindfaas-worker
    deployment.spec.template.spec.node_selector["kubernetes.io/hostname"] = cnodes[0]
    resp = api_v1.patch_namespaced_deployment(
        name=deployment_name, namespace="openfaas-fn", body=deployment
    )
    print("\n[INFO] deployment's container image updated.\n")
    print("%s\t%s\t\t\t%s\t%s" % ("Namespace", "Name", "Node"))
    print(
        "%s\t\t%s\t\t%s\n"
        % (
            resp.metadata.namespace,
            resp.metadata.name,
            resp.spec.template.spec.node_selector,
        )
    )


# Query every 15 seconds
while True:
    reschedulingNeeded = False
    sortedNodesByScore = []
    nodes = []
    # functions = []
    row = 0

    r1 = requests.get(url=const.url, params=const.query["mem_usage"])
    r2 = requests.get(url=const.url, params=const.query["cpu_usage"])

    mem_json = r1.json()["data"]["result"]
    cpu_json = r2.json()["data"]["result"]

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
    # if reschedulingNeeded:
    if reschedulingNeeded:
        print("#####RESCHEDULING####")
        r3 = requests.get(
            url=const.url, params=const.query["function_invocation_per_minut"]
        )
        functions_json = r3.json()["data"]["result"]
        # INFO low_score to higher_score
        sortedNodesByScore = sorted(
            nodes_info, key=lambda node_name: (nodes_info[node_name].get_score())
        )
        print(sortedNodesByScore)
        for result in functions_json:
            function_name = (
                result["metric"].get("function_name", "").split(const.delimetar)[0]
            )
            invocation = float(result["value"][1])
            faas_functions[function_name] = FaasFunc(invocation)

        pod_list = v1.list_namespaced_pod("openfaas-fn")
        for pod in pod_list.items:
            function_name = pod.metadata.labels["faas_function"]
            faas_functions[function_name].set_node(pod.spec.node_name)
        critical_functions = dict()
        print(sortedNodesByScore[len(sortedNodesByScore) - 1])
        for key in faas_functions:
            print(faas_functions[key].get_node())
            print(sortedNodesByScore[len(sortedNodesByScore) - 1])

            if (
                faas_functions[key].get_node()
                == sortedNodesByScore[len(sortedNodesByScore) - 1]
            ):
                print(
                    "Funtion {key} is on critical node {faas_functions[key].get_node()}"
                )
                critical_functions[key] = faas_functions[key].get_invocation()

        if bool(critical_functions):
            print("There is one or more functions on critical nodes.")
            sortedFunctioncsByInvocation = sorted(
                critical_functions, key=lambda func_name: func_name[1], reverse=True
            )
            print(sortedFunctioncsByInvocation)
            deployment = api_v1.read_namespaced_deployment(
                name=sortedFunctioncsByInvocation[0], namespace="openfaas-fn"
            )
            rescheduleDeployment(
                api_v1, deployment, sortedFunctioncsByInvocation[0], sortedNodesByScore
            )
            print(sortedNodesByScore)
        else:
            print("All functions are executing on non critical nodes.")
        print("AS")

    # TODO remove print, it is using for debugging
    print("\n[INFO] Memory and CPU usage in %.\n")
    print("instance \t| memory \t\t| cpu")
    for node in nodes:
        line = str(node[0]) + " | " + str(node[1]) + " | " + str(node[2])
        print(str(line))
    sys.stdout.flush()

    print("#######################")
    time.sleep(15)
