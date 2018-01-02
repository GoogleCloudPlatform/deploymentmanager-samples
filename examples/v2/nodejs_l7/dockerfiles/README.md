# Dockerfiles

Supporting files for the HTTP Load-balanced Logbook tutorial.

* `service.js`: NodeJS static service, located at `/static` in the deployed application.
* `Dockerfile`: Dockerfile to build the `nodejsservicestatic` image.

The tutorial also uses [the `mysql` and `nodejsservice` images](../../nodejs/dockerfiles) from the Network Load-balanced Logbook tutorial. 

For steps to build and upload the Docker images, see [the tutorial](https://cloud.google.com/deployment-manager/docs/create-advanced-http-load-balanced-deployment#create_docker_images).
