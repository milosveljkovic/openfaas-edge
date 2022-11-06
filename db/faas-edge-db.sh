#!/bin/bash
kubectl apply -f faas-edge-db-init-config.yaml -n default

sleep 5

helm repo add bitnami https://charts.bitnami.com/bitnami && \
helm install faas-edge-db bitnami/postgresql --values ./postgres-helm-values.yaml

kubectl port-forward --namespace default svc/faas-edge-db-postgresql 5432:5432 &

echo "Please kill bg process which listen on 5432 port"