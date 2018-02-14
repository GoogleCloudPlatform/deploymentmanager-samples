# Dockerfiles

Supporting files for the [Network Load-balanced Logbook tutorial](https://cloud.google.com/deployment-manager/docs/create-advanced-deployment)

[mysql](mysql):
* `startup.sh`: Startup script for the MySQL container
* `Dockerfile`: Dockerfile to build the MySQL container

[node](node):
* `service.js`: Example NodeJS logbook service
* `Dockerfile`: Dockerfile to build the `nodejsservice` container

## Building the Docker images

If you want to modify the example Node.js application, or use your own repository
for your Docker images, you must re-build the Docker images, and upload them to
your Google Container Registry, or to a Docker Hub repository.

### Before you begin

* If you are using Google Container Registry to store your Docker images, enable
  the [Container Registry API](https://console.cloud.google.com/apis/api/containerregistry.googleapis.com/overview).
* If you are using Docker Hub to store the images, create a [Docker
  Hub](https://hub.docker.com/) account.
* To build the images, you can use [Cloud Shell](https://cloud.google.com/shell/)
  which has the prerequisites to build and upload Docker images. If you want to
  use your own workstation, install:
  * Docker Engine. For steps, see the [Docker documentation](https://docs.docker.com/engine/installation/).
  * The `gcloud` command-line tool. For steps to install and configure the tool,
  see the [Cloud SDK documentation](https://cloud.google.com/sdk/docs/quickstarts).


### Building the images

1. Configure the `gcloud` command-line tool to use your project. In the following
   command, replace `[PROJECT-ID]` with your project ID:

    ```sh
    gcloud config set project [PROJECT-ID]
    ```

1. On your machine, create a new directory for the `mysql` image:

    ```sh
    mkdir mysql
    cd mysql
    ```
1. Download the Dockerfile and startup script for the MySQL image:

    ```sh
    wget https://raw.githubusercontent.com/GoogleCloudPlatform/deploymentmanager-samples/master/examples/v2/nodejs/dockerfiles/mysql/startup.sh

    wget https://raw.githubusercontent.com/GoogleCloudPlatform/deploymentmanager-samples/master/examples/v2/nodejs/dockerfiles/mysql/Dockerfile
    ```

1. Build the Docker image:

    ```sh
    sudo docker build - t tutorial-mysql-image .
    ```

1. If you are uploading the image to [Google Container Registry](https://cloud.google.com/container-registry/), tag the image so that it can be uploaded:

    ```sh
    docker tag tutorial-mysql-image gcr.io/[PROJECT-ID]/tutorial-mysql-image
    ```

  If you want to upload your image to Docker Hub, see the
  [Docker Hub documentation](https://docs.docker.com/docker-hub/).

1. Push the image to Container Registry:

    ```sh
    gcloud docker -- push gcr.io/[PROJECT-ID]/tutorial-mysql-image
    ```

1. In the [Node.js template](../../python/nodejs.py), replace the `dockerImage`
   property with the image you built above.

1. Repeat the above steps to build the image for the Node.js application, using
   the following Dockerfile and application script:

    ```sh
    wget https://raw.githubusercontent.com/GoogleCloudPlatform/deploymentmanager-samples/master/examples/v2/nodejs/dockerfiles/node/Dockerfile

    wget https://raw.githubusercontent.com/GoogleCloudPlatform/deploymentmanager-samples/master/examples/v2/nodejs/dockerfiles/node/service.js
    ```
