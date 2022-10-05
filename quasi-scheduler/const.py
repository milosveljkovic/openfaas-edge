
# query['mem'] - returns usage of memory in %
# query['cpu'] - returns usage of CPU in %

query = dict(
    mem = {'query':'(node_memory_MemTotal_bytes - (node_memory_MemFree_bytes + node_memory_Cached_bytes + node_memory_Buffers_bytes)) / node_memory_MemTotal_bytes * 100'},
    cpu = {'query':'100 - avg(irate(node_cpu_seconds_total{job="node-exporter",mode="idle"}[5m])) by (instance) * 100'},
    function_invocation_per_minut= {'query':'rate( gateway_function_invocation_total [1m])'}
)

url = "http://localhost:9090/api/v1/query"

delimetar="."