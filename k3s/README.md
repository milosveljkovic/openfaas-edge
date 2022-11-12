#### K3S notes

When k3s has been deployed, deploy openfaas and node-exporter.

If you are facing some issue with node-exporter's pods, run following:

ssh into server using vagrant ssh

```sh
vagrant ssh server && sudo su && mount --make-rshared /
```

ssh into agent1 using vagrant ssh

```sh
vagrant ssh agent1 && sudo su && mount --make-rshared /
```

ssh into agent2 using vagrant ssh

```sh
vagrant ssh agent2 && sudo su && mount --make-rshared /
```

etc..

If you want to deploy prometheus configMap with node-exporter fields, deploy configMap from additinal_config

If you want to patch prometheus deployment, run following command:

```sh
kubectl patch deployment prometheus --patch-file prometheus-patch.yaml -n openfaas
```