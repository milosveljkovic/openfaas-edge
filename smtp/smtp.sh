
#!/bin/bash
kubectl apply -f mysql-initdb-config.yaml -n default

sleep 5

helm repo add bitnami https://charts.bitnami.com/bitnami
helm install smtp-db-mysql bitnami/mysql --values ./smtp-sql-helm-values.yaml

kubectl apply -f smtp-dep.yaml -n default

sleep 30

kubectl port-forward svc/smtp-service -n default 8085 &

kubectl port-forward svc/smtp-service -n default 8081:8080

echo "Please kill bg processess which listen on 8085 and 8081"