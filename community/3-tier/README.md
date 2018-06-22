- [GCP_Deployment_Manager_Samples](#gcp-deployment-manager-samples)
  * [Disclaimer: Don't take this as gospel!!](#disclaimer--don-t-take-this-as-gospel--)
  * [What is this?](#what-is-this-)
  * [Tidy Up](#tidy-up)
  * [Known Issues](#known-issues)
  * [What does this deploy?](#what-does-this-deploy-)
  * [To Do](#to-do)

<small><i><a href='http://ecotrust-canada.github.io/markdown-toc/'>Table of contents generated with markdown-toc</a></i></small>

# GCP_Deployment_Manager_Samples
Sample repo to deploy a 3 tier web app to GCP using Deployment Manager

## Disclaimer: Don't take this as gospel!!
These scripts are an example of how to use Deployment Manager to deploy a 3 tier web-app, specifically this web app: https://github.com/Sufyaan-Kazi/spring-boot-cities-service and this one: https://github.com/Sufyaan-Kazi/spring-boot-cities-ui. They are not a BEST practice way of doing it and certainly should NOT be used for production ready code!

## What is this?
There are two scripts - one "generic" ish script called ```dmFunctions.sh```. This has "generic" ish functions to deploy different types of gcloud objects such as load balancers, health-checks etc using jinja templates. The other script is a wrapper called ```deployCitiesMicroServices.sh``` which is not generic. It specifcally calls methods from ```dmFunctions.sh``` to deploy the two 'cities' microservices"

The automation uses jinja templates. For example, the 'it.jinja' file is a template to deploy a compute instance, since it is a template it has placeholders for parameters like instance name, network etc.

When ```deployCitiesMicroServices.sh``` is run, it reads in variables from the file 'vars.properties' which defines properties like network, instance name etc and these become shell variables, which can then be passed to the call to the deployment manager with each template.

In a real world, these two microservices would actualy be deployed as containers using K8S, PCF, OpenShift or a.n.other. This is an example of how to automate deployment in a non-containersied world using pure IaaS on GCP.

N.B. The sub-directory 'old' is an example of deployment NOT using jinja and just plain old yaml for all the objects. In this method there is a lot of duplication of yaml .....

## Tidy Up
To remove all the deployments made by this script, run ```cleanup.sh```. When you run ```deployCitiesMicroserVice.sh```, it calls this script anyway.

## Known Issues
If you deploy this to a GCP project that has some kind of auotmated firewall enforcement to stop all instances having external access by default etc, then the app will still deploy and be reachable correctly. However, the startup will be longer and may need an additional 5-10 minutes to be completely ready even after the script finishes.

## What does this deploy?

![Cities](/DepManager.png)
* An instance group with health-checks, autoscaling etc for the cities-service microservice, including an internal TCP load balancer to distribute traffic over this group.
* An instance group with health-checks, autoscaling etc for the cities-ui microservice, including an external HTTP load balancer to distribute traffic to this web layer
* Firewall rules to allow the web layer to communicate with the back-end layer
* Firewall rules to enable both health-checks and load balancers to communicate with each of their instance groups

## To Do
* Modify the script to create an instance image for the common aspects of the compute instances, and make the two instances refer to that image as the source, to reduce startup time and duplication.
* Insert some kind of discovery service layer so the ip address of the internal load balancer is invisible to the web layer
* Remove the need to "discover" the ip address of the internal load balancer and to "inject" it into the deployment of the cities-ui as a dependency
* Use CloudSQL or a.n.other as the third tier rather than H2 as the Spring Boot apps currently do
* Serve the static content from a bucket and dynamic content from compute, with CDN layer in front.
