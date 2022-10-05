#!/bin/sh

# Author : Milos Veljkovic
# Description: Setup script which set-up all components in kind k8s (ingress,openfaas,exporter etc)

if ! command -v kubectl &> /dev/null
then
    echo
    echo "Command kubectl could not be found. Please install it."
    echo 
    exit 1
fi

if ! command -v helm &> /dev/null
then
    echo
    echo "Command helm could not be found. Please install it."
    echo 
    exit 1
fi

K8S_CONTEXT=$(kubectl config current-context)

while true; do
    read -p "Your current k8s context is ${K8S_CONTEXT}. Do you wish to proceed ? [y/n]" yn
    case $yn in
        [Yy]* ) break;;
        [Nn]* ) exit 1;;
        * ) echo "Please answer y(yes) or n(no).";;
    esac
done

echo
echo "Installing nginx ingress.."
echo

kubectl apply -f https://raw.githubusercontent.com/kubernetes/ingress-nginx/main/deploy/static/provider/kind/deploy.yaml

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during ingress installation."
  exit 1
fi

echo
echo "Installing test app to make sure the ingress is working properly."
echo

kubectl apply -f https://kind.sigs.k8s.io/examples/ingress/usage.yaml

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during test-app installation."
  exit 1
fi

echo
echo "Test ingress. Open localhost/foo in browser!"
echo

echo
echo "Openfaas installation.."
echo "Create namespaces: openfaas & openfaas-functions"
echo

kubectl apply -f https://raw.githubusercontent.com/openfaas/faas-netes/master/namespaces.yml

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during creation of openfaas namespaces."
  exit 1
fi

echo
echo "Add openfaas repo with helm & update repo."
echo

helm repo add openfaas https://openfaas.github.io/faas-netes/
helm repo update

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during helm add/update."
  exit 1
fi

echo
echo "Generate password for openfaas gateway app."
echo

export PASSWORD=$(head -c 12 /dev/urandom | shasum| cut -d' ' -f1)

echo
echo "Openfaas PASSWORD=${PASSWORD}"
echo "Create k8s secret for openfaas."
echo

kubectl -n openfaas create secret generic basic-auth --from-literal=basic-auth-user=admin --from-literal=basic-auth-password="$PASSWORD"

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during creation of openfaas secret."
  exit 1
fi

echo
echo "Install openfaas with helm."
echo

helm upgrade openfaas --install openfaas/openfaas --namespace openfaas --set functionNamespace=openfaas-fn --set basic_auth=true

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during openfaas installation."
  exit 1
fi

echo
echo "Use following commnad to port-forward openfaas-gateway and login with creds: admin/${PASSWORD}"
echo "kubectl port-forward svc/gateway -n openfaas 8080:8080"
echo

echo
echo "Create PrometheusClusterRole."
echo

kubectl create -f ../additional_config/PrometheusClusterRole.yaml

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during creation of PrometheusClusterRole."
  exit 1
fi

echo
echo "Create Node Exporter as a daemonset."
echo

kubectl create -f ../node-exporter/daemonset.yaml

if [ $? -gt 0 ]; then
  echo "Somethin went wrong during creation of  Node Exporter."
  exit 1
fi

echo
echo "That's all falks."
echo