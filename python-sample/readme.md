# How to upload images to local openshift image registry

```
docker login -u `oc whoami` -p `oc whoami --show-token` https://default-route-openshift-image-registry.apps.baseline-parth.5kj1.p1.openshiftapps.com
oc new-project python-sample
oc create imagestream python-sample
docker tag python-sample:latest default-route-openshift-image-registry.apps.parth-test.swew.p1.openshiftapps.com/python-sample/python-sample:latest
docker push default-route-openshift-image-registry.apps.parth-test.swew.p1.openshiftapps.com/python-sample/python-sample:latest
```

https://cookbook.openshift.org/image-registry-and-image-streams/how-do-i-push-an-image-to-the-internal-image-registry.html
