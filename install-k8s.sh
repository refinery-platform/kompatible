#!/usr/bin/env bash
set -o errexit
set -o nounset

# Tips for Kubernetes on Travis come from:
# https://blog.travis-ci.com/2017-10-26-running-kubernetes-on-travis-ci-with-minikube
# Later updated by:
# https://github.com/LiliC/travis-minikube/blob/master/.travis.yml

# This moves Kubernetes specific config files.
export CHANGE_MINIKUBE_NONE_USER=true
JSONPATH='{range .items[*]}{@.metadata.name}:{range @.status.conditions[*]}{@.type}={@.status};{end}{end}'

# Download kubectl, which is a requirement for using minikube.
curl -Lo kubectl https://storage.googleapis.com/kubernetes-release/release/$KUBERNETES_VERSION/bin/linux/amd64/kubectl \
  && chmod +x kubectl && sudo mv kubectl /usr/local/bin/

# Download minikube.
curl -Lo minikube https://storage.googleapis.com/minikube/releases/v0.25.2/minikube-linux-amd64 \
  && chmod +x minikube && sudo mv minikube /usr/local/bin/
sudo minikube start --vm-driver=none --kubernetes-version=$KUBERNETES_VERSION

# Fix the kubectl context, as it's often stale.
minikube update-context

# Wait for Kubernetes to be up and ready.
until kubectl get nodes -o jsonpath="$JSONPATH" 2>&1 | grep -q "Ready=True"; do
  sleep 1
  echo "waiting for kubernetes"
done

kubectl cluster-info

# Verify kube-addon-manager.
# kube-addon-manager is responsible for managing other kubernetes components, such as kube-dns, dashboard, storage-provisioner..
until kubectl -n kube-system get pods -lcomponent=kube-addon-manager -o jsonpath="$JSONPATH" 2>&1 | grep -q "Ready=True"; do
  sleep 1
  echo "waiting for kube-addon-manager"
  kubectl get pods --all-namespaces
done

# Wait for kube-dns to be ready.
until kubectl -n kube-system get pods -lk8s-app=kube-dns -o jsonpath="$JSONPATH" 2>&1 | grep -q "Ready=True"; do
  sleep 1
  echo "waiting for kube-dns"
  kubectl get pods --all-namespaces
done
