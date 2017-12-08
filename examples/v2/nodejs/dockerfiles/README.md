# Dockerfiles

Supporting files for the Network Load-balanced Logbook tutorial

[mysql](mysql):
* `startup.sh`: Startup script for the MySQL container
* `Dockerfile`: Dockerfile to build the MySQL container

[node](node):
* `service.js`: Example NodeJS logbook service 
* `Dockerfile`: Dockerfile to build the `nodejsservice` container

For steps to build and upload the Docker images, see [the tutorial](https://cloud.google.com/deployment-manager/docs/create-advanced-deployment#create_docker_images).
