# How to upload images to local openshift image registry

```
docker login -u `oc whoami` -p `oc whoami --show-token` registry.pro-us-east-1.openshift.com:443
oc new-project python-sample
oc create imagestream python-sample
docker tag python-sample:latest default-route-openshift-image-registry.apps.parth-test.swew.p1.openshiftapps.com/python-sample/python-sample:latest
docker push default-route-openshift-image-registry.apps.parth-test.swew.p1.openshiftapps.com/python-sample/python-sample:latest
```