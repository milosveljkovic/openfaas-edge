# query['mem'] - returns usage of memory in %
# query['cpu'] - returns usage of CPU in %

query = dict(
    mem_usage={
        "query": "(node_memory_MemTotal_bytes - (node_memory_MemFree_bytes + node_memory_Cached_bytes + node_memory_Buffers_bytes)) / node_memory_MemTotal_bytes * 100"
    },
    cpu_usage={
        "query": '100 - avg(irate(node_cpu_seconds_total{job="node-exporter",mode="idle"}[5m])) by (node_name) * 100'
    },
    function_invocation_per_minut={
        "query": "rate( gateway_function_invocation_total [1m])"
    },
    total_memory={"query": " node_memory_MemTotal_bytes"},
)

url = "http://localhost:9090/api/v1/query"

delimetar = "."
