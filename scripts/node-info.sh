# Deploy openfaas function which get node-info
# This function is used only for testing purpose
# Before deploying you should port-forward gateway:8080
# Before deploying faas-cli login -u amin -p <basic_auth_secret>
# target: 50 RPS
# 90% utilization of target

faas-cli store deploy nodeinfo \
--label com.openfaas.scale.max=10 \
--label com.openfaas.scale.target=50 \
--label com.openfaas.scale.type=rps \
--label com.openfaas.scale.target-proportion=0.90 \
--label com.openfaas.scale.zero=true \
--label com.openfaas.scale.zero-duration=10m

# Run for 3 minutes
# With 5 concurrent callers
# Limited to 20 QPS per caller
hey -z 3m -c 5 -q 20 \
  http://127.0.0.1:8080/function/nodeinfo