import requests
import time
import sys
import const
from kubernetes import config , client


config.load_kube_config()
v1 = client.CoreV1Api()

class FaasFunctions(dict):
  # __init__ function
  def __init__(self):
    self = dict()
 
  # Function to add key:value
  def add(self, key, value):
    self[key] = value

faas_functions=FaasFunctions()

class FaasFunc:
  def __init__(self, invocation, node=-1):
    self.invocation = invocation
    self.node = node
  
  def set_invocation(self, new_invocation):
    self.invocation=new_invocation
  def set_invocation(self):
    return self.invocation

  def set_node(self, node):
    self.node=node
  def get_node(self):
    return self.node

#Query every 15 seconds 100 times
while True:
  nodes = []
  # functions = []
  row = 0

  r1 = requests.get(url = const.url, params = const.query['mem'])
  r2 = requests.get(url = const.url, params = const.query['cpu'])
  r3 = requests.get(url = const.url, params = const.query['function_invocation_per_minut'])

  mem_json = r1.json()['data']['result']
  cpu_json = r2.json()['data']['result']
  functions_json = r3.json()['data']['result']

  for result in mem_json:
    instance= result['metric'].get('instance', '')
    mem=result['value'][1]
    nodes.append([instance,mem])

  for result in cpu_json:
    cpu=result['value'][1]
    nodes[row].append(cpu)
    row = row + 1

  for result in functions_json:
    function_name= result['metric'].get('function_name', '').split(const.delimetar)[0]
    invocation=result['value'][1]
    faas_functions.add(function_name,FaasFunc(invocation))
    # functions.append([function_name,invocation])

  pod_list = v1.list_namespaced_pod('openfaas-fn')
  for pod in pod_list.items:
    function_name=pod.metadata.labels['faas_function']
    faas_functions[function_name].set_node(pod.spec.node_name)

  print("instance | memory | cpu")
  for node in nodes:
      line = node[0] + " | " + node[1] + " | " + node[2]
      print(str(line))
  sys.stdout.flush()



  print('#######################')
  time.sleep(5)