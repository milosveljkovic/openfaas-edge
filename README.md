# Openfaas-edge system
Openfaas edge system for smart-home.

# Development

### K3S config

Set-up your k3s cluster:

sh
```
cd k3s && mkdir shared && vagrant up
```

When cluster has been deployed, deploy openfaas (you do not need ingress) and other stuf.

### KIND config

Start kind with 2 nodes (control plane & worker)

```sh
kind create cluster --config additional_config/multi-node-cluster.yaml
```

##### Automated

The following script will prepare cluster for you (install ingress, openfaas, node-exporter):

```sh
./scripts/setup.sh
```

##### Manually

If you decide to install each pre-req part manually, follow instructions bellow:

First, install Ingress & test it with some dummy app

**Install NGINX Ingress:**

  - Deploy ingress with following script:
  ```sh
  kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml
  ```

- Install app which helps to test ingress:
  ```sh
  kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/usage.yaml
  ```
Test ingress: open in browser `localhost/foo` (you should get foo as a response)

**Note:** If something went wrong just restart (delete) whole cluster, then try again.

**Install openfaas:**

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

**How to connect to openfaas:**
- When OpenFaas has been deployed, if you want to communicate with gateway, you should port-forward gateway svc, then login using faas-cli login:
  ```sh
  kubectl port-forward svc/gateway -n openfaas 8080
  ```
- Set the `OPENFAAS_URL` env-var export `OPENFAAS_URL=localhost:8080`
- Finally once all the Pods are up&running you can login using the CLI
  ```sh
  echo -n $PASSWORD | faas-cli login -g http://$OPENFAAS_URL -u admin — password-stdin
  ```
At the end, in your KIND cluster you should have two namespaces: `openfaas` and `openfaas-fn`.

**Openfaas notes:**

Build, push (login to docker hub required) & deploy function:

```sh
faas-cli build -f function_name.yml && \
docker push milosveljkovic97/function_name:TAG && \
faas-cli deploy -f function_name.yml
```

Note that next to openfaas component, Prometheus has been deployed and require additional configuration.

**Prometheus additional configuration:**

Prometheus deployed alongside with openfaas is configured to works with two namespaces: `openfaas` and `openfaas-fn`.

As we will use Prometheus to decide when our cluster is overwhelmed, we have to extend Prometheus configuration in a way to provide observation of full cluster metrics (nodes metrics).

We should deploy `ClusterRole` and `ClusterRoleBinding` from `additional_config` directory.
```sh
kubectl create -f additional_config/PrometheusClusterRole.yaml
```

After deploying `ClusterRole` and `ClusterRoleBinding`, deployment `prometheus` from `openfaas` namespace has to be updated.

deployments/prometheus.yaml
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

**Node exporter:**

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
    - source_labels: [__meta_kubernetes_endpoint_node_name]
      action: replace
      target_label: node_name
```

**Deploy PostgreSQL:**

Fast way of doing it (required export KUBECONFIG): 

```sh
cd db && ./faas-edge-db.sh
```

but if you want to deploy it manually, go ahead:

Faas-edge deeply depends on postgresql db, so we have to deploy it in our KIND cluster:

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami && \
helm install faas-edge-db bitnami/postgresql
```

When db has been deployed, connect to it (instructions bellow) and execute query from db/faas-edge-db.sql script.

PostgreSQL can be accessed via port 5432 on the following DNS names from within your cluster:

```sh
faas-edge-db-postgresql.default.svc.cluster.local
```

To get the password for "postgres" run:

```sh
export POSTGRES_PASSWORD=$(kubectl get secret --namespace default faas-edge-db-postgresql -o jsonpath="{.data.postgres-password}" | base64 -d)
```

To connect to your database run the following command:

```sh
kubectl port-forward --namespace default svc/faas-edge-db-postgresql 5432:5432
```

**Deploy smtp:**

Run following script to set-up smtp stack with script (required export KUBECONFIG):

```sh
cd smtp && ./smtp.sh
```

or set-up smtp stack manually:

Smtp server relies on mysql, so we need to deploy that part first.

```sh
helm repo add bitnami https://charts.bitnami.com/bitnami && \
helm install smtp-db-mysql bitnami/mysql
```

When db has been deployed, port-forward svc to localhost (then connect to it):

```sh
kubectl port-forward svc/smtp-db-mysql -n default 3306
```

Connection info:

```
ServerHost: localhost
Port: 3306
Database: (leave it empty)
Username: root
Password: find pass in k8s secret
```

When connected to db, execute script from db/smtp.sql.

Before deploying smrt server, update config in smtp/smtp-dep.yaml file to meet your mysqlDB requirements.

```yaml
apiVersion: v1
kind: ConfigMap
metadata:
  name: smtp-config
  namespace: default
data:
  config.json: |
    {
    "wwwAddress": "0.0.0.0",
    "wwwPort": 8080,
    "serviceAddress": "0.0.0.0",
    "servicePort": 8085,
    "smtpAddress": "0.0.0.0",
    "smtpPort": 2500,
    "dbEngine": "MySQL",
    "dbHost": "smtp-db-mysql",
    "dbPort": 3306,
    "dbDatabase": "my_database",
    "dbUserName": "root",
    "dbPassword": "UPDATE_THIS_WITH_PASS_FROM_K8S_SECRET",
    "maxWorkers": 1000
    }
```

Then deploy it, and port-forward (choose different port if 8080 is taken):

```sh
kubectl port-forward svc/smtp-service -n default 8085
kubectl port-forward svc/smtp-service -n default 8080 # 8081:8080
```

**Functions:**

Update DB string in storing and reporting functions.