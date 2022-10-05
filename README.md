# Openfaas-edge system
Openfaas edge system with extended prometheus.

# Development

### KIND config

#### Start kind with 2 nodes (control plane & worker)

```sh
kind create cluster --config additional_config/multi-node-cluster.yaml
```
#### Install ingress, openfaas, node-exporter with script

```sh
./scripts/setup.sh
```

#### MANUALLY
#### Install Ingress & test it with some dummy app

Install NGINX Ingress:
```sh
kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
```

Install app which helps to test ingress:
```sh
kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/usage.yaml
```
Test ingress - open in browser `localhost/foo` (you should get foo as a response)

### minikube configuration & instalation

#### Start minikube:
```sh
minikube start --addons=ingress
```

### Install openfaas:

- Create namespaces for OpenFaaS core components and OpenFaaS Functions
  ```sh
  kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml
  ```
- Add the OpenFaaS helm repository
  ```sh
  helm repo add openfaas https://openfaas.github.io/faas-netes/
  ```
- Update all the charts for helm
  ```sh
  helm repo update
  ```
- Generate a random password
  ```sh
  export PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)
  ```
- Create a secret for the password
  ```sh
  kubectl -n openfaas create secret generic basic-auth --from-literal=basic-auth-user=admin --from-literal=basic-auth-password="$PASSWORD"
  ```
- Install OpenFaaS using the chart
  ```sh
  helm upgrade openfaas --install openfaas/openfaas --namespace openfaas --set functionNamespace=openfaas-fn --set basic_auth=true
  ```
- Set the `OPENFAAS_URL` env-var export `OPENFAAS_URL=$(minikube ip):31112`
- Finally once all the Pods are started you can login using the CLI
  ```sh
  echo -n $PASSWORD | faas-cli login -g http://$OPENFAAS_URL -u admin — password-stdin
  ```
At the end, in your minikube cluste you should have `two` namespaces: `openfaas` and `openfaas-fn`.
Next to openfaas component, you can notice that Prometheus has been deployed and require additional configuration.

#### Prometheus additional configuration

Prometheus deployed alongside with openfaas is configured to works with two namespaces: `openfaas` and `openfaas-fn`.

As we will use Prometheus to decide when our cluster is overwhelmed, we have to extend Prometheus configuration in a way to provide observation of full claster metrics (nodes metrics!!!).

We should deploy `ClusterRole` and `ClusterRoleBinding` from `additiona_config` directory.

```sh
kubectl create -f additiona_config/PrometheusClusterRole.yaml
```

After deploying `ClusterRole` and `ClusterRoleBinding`, deployment `prometheus` from `openfaas` ns has to be updated.

prometheus.yaml
```yaml
kind: Deployment
apiVersion: apps/v1
metadata:
  name: prometheus
  namespace: openfaas
...
serviceAccountName: prometheus-sa
serviceAccount: prometheus-sa
```

#### Node exporter

Prometheus use exporters for exporting existing metrics from third-party systems.

We are using [Node exporter](https://github.com/prometheus/node_exporter) which can expose k8s nodes metrics (cpu/mem_usage etc).

```sh
kubectl create -f node-exporter/daemonset.yaml
```

If you want Prometheus to watch those exporters, you have to update prometheus configmap.

- Add new job
- relabele_config

prometheus-config.yaml
```yaml
  - job_name: 'node-exporter'
    kubernetes_sd_configs:
      - role: endpoints
    relabel_configs:
    - source_labels: [__meta_kubernetes_endpoints_name]
      regex: 'node-exporter'
      action: keep  
```

