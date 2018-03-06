# edge-gcp
This project allows you to install Edge in Google Cloud Platform using GCP's deployment manager.
This is will install aio instance of edge along with dashboard monitoring and a dev portal.

## Prerequisite

### gcloud
- Install gcloud sdk from https://cloud.google.com/sdk/downloads
- Initialize your account

## Before you start
- Edit the aio/jinja/apigee-edge.yaml and update the properies

    ```sh
        aio-config: aio-config.txt
        machineType: [ machine type  e.g: n1-highcpu-8]
        zone: [ zone e.g : us-central1-b]
        softwareRepo: https://software.apigee.com
        version: '4.17.01'
        repo:
           host: software.apigee.com
           protocol: https
           user: apigee
           password: mypasswordToAccessRepo
           stage: release
        license: "[your license]" #Paste the contents of license file.
    ```
- Change the silent config file entries present in aio/jinja/aio-config.txt

## Deploy AIO profile
```sh
./deploy.sh "RESOURCE_NAME" 
```
e.g :
```sh
./deploy.sh apigee-edge
```

## Undeploy and Clean the deployment
```sh
./clean.sh "RESOURCE_NAME"
```
e.g :
```sh
./clean.sh apigee-edge
```
## License

Apache 2.0 - See [LICENSE](LICENSE) for more information.

