# Howto deploy KUBERNETES PUSHNOTIFICATION services into azure KUB cluster

## Introduction

This containes all the services and deployment yaml files required to deploy the PUSHNOTIFICATION infra to KUB cluster

## REQUIREMENTS

### AZURE-CLI

#### MACOSX

```bash
brew update && brew install azure-cli
``` 

#### LINUX

```bash
AZ_REPO=$(lsb_release -cs)
$echo "deb [arch=amd64] https://packages.microsoft.com/repos/azure-cli/ $AZ_REPO main" | \
    sudo tee /etc/apt/sources.list.d/azure-cli.list
    
```

```bash
$curl -L https://packages.microsoft.com/keys/microsoft.asc | sudo apt-key add -
$sudo apt-get update
$sudo apt-get install apt-transport-https azure-cli
```
To check if is working:

```bash
az login
```

### KUBERNETES-CLI

#### MACOSX

```bash
brew onstall kubernetes-cli
```

#### LINUX

```bash
$sudo apt-get update && sudo apt-get install -y apt-transport-https
$curl -s https://packages.cloud.google.com/apt/doc/apt-key.gpg | sudo apt-key add -
$echo "deb http://apt.kubernetes.io/ kubernetes-xenial main" | sudo tee -a /etc/apt/sources.list.d/kubernetes.list
$sudo apt-get update
$sudo apt-get install -y kubectl
```

To check if is working:

```bash
kubectl version
```

### Azure registry and KUBE cluster

ATM we use hostbla.azurecr.io for docker registry and blaaksclu01 as KUB cluster

## DEPLOYMENT

### BUILD docker images

First step is to build the docker images required for the service to run

```bash
$ docker build -t eg_pushnotif .
```

!!!NB!!! do the same for all services: mem, nginx, stats, mock (Check the docker directories

Check the images:


```bash
$ docker image ls
REPOSITORY                                               TAG                 IMAGE ID            CREATED             SIZE
[...]
```

### TAG and PUSH the images

```bash
$ docker tag eg_pushnotif host.io/eg_pushnotif
$ docker push host.io/eg_pushnotif
```

To check if the image was PUSHED:

```bash
$ docker pull hostbla.azurecr.io/eg_pushnotif

```

```bash
$ docker image ls
```

## Create dev namespace

Best practice is to use your own namespace (!!!NB!!! by default all services are using default namespace)

```bash
$ kubeclt create -f namespace-dev.json
```

To check if namespace is created run:

```bash
$ kubectl get namespaces --show-labels
```


More info about the [topic](https://kubernetes.io/docs/tasks/administer-cluster/namespaces-walkthrough/)

!!!NB!!!!

Don't forget to add the namespace in the services yaml files

```
kind: Service
metadata:
  name: my-app
  namespace: my-namespace
  labels:
    app: my-app
```

### DEPLOY YAML files to KUB cluster

```bash
$ kubectl create -f *-deployment.yaml
$ kubectl create -f *-service.yaml
```

Where   = mem, mock, nginx, push, stats

Check if services are deployed

```bash
$kubectl get svc
```

Check if pods are deployed

```bash
$kubectl get pods
```

Get the IP of the nginx service

```bash
$ kubectl describe service nginx
```

Output should look like this:

```
Name:              nginx
Namespace:         default
Labels:            io.kompose.service=nginx
Annotations:       kompose.cmd=kompose convert
                   kompose.version=1.16.0 ()
Selector:          io.kompose.service=nginx
Type:              ClusterIP
IP:                10.0.60.85
Port:              8080  8080/TCP
TargetPort:        8080/TCP
Endpoints:         XXXXX:8080
Session Affinity:  None
Events:            <none>
```

## TESTING

If all services are up&running

## Register a jobid to the pushnotification service

```bash
$ curl 'http://xxxxx:8080/push?userid=dan&ticket=host.com&jobid=123'
```

### Get notification via websockets

```bash
wscat --connect ws://xxxxx:8080/register?userid=dan
```

## MISCELLANEOUS

## Browse KUB cluster using the proxy

```bash
kubectl browse
``` 

Open the browser and click [here](http://localhost:8001/api/v1/namespaces/kube-system/services/kubernetes-dashboard/proxy/#!/overview?namespace=default)


Another way how to use the proxy is:

```bash
az aks get-credentials --resource-group bla-it-aks-prd --name blaaksclu01
```

## AUTH ISSUES publishing docker

If when pushing the docker image the process will fail because there is some auth issue:

```bash
az login
az acr login --name hostbla
az aks get-credentials --resource-group aks --name xxx
```

## DELETING PODS

In order to delete a pod, first the deployement must be deleted, if not the KUB cluster will spin up another pod

EX:

```bash
$ kubectl delete deployments push
$ kubectl delete pods push*
```

Or use the -f yaml file
```bash
$ kubectl delete -f *-deployment.yaml
$ kubectl delete -f *-service.yaml
```



