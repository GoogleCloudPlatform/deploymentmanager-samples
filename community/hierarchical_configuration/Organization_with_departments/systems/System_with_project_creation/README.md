# Loading external templates without modification

## Summary
Creating Symbolic links for external folders, maybe from other repositories, makes it possible to integrate external 
templates easily to your deployment. This avoids to duplicate the codebase of the external template as well to hardcode the path
where the template is located at your filesystem in the schema file. ( Instead of this, it's hardcoded in the initialization 
command which creates the Symbolic Link.)
 
 
 ### System setup
 
 The following Symbolic links are putting the appropriate global configurations to the right path:
 
 ```bash
ln -s ../../../../../../examples/v2/project_creation templates/project_creation

```







## WORKING EXAMPLE TODO FIX

```bash

# These 5 commands will get you up and running! This will deploy Dev,Test, Prod env as specified in the CLI argument
$ git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples.git
$ cd deploymentmanager-samples/community/hierarchical_configuration/Organization_with_departments/systems/my_ecom_system
# set project_id <your-personal-project-id> # (or add it to next gcloud commands)
# Deploy Dev example
$ gcloud deployment-manager deployments create hierarchy-org-example-dev --template env_demo_project.py --properties=envName:dev
# Deploy Test example
$ gcloud deployment-manager deployments create hierarchy-org-example-test --template env_demo_project.py --properties=envName:test
# Deploy Prod example
$ gcloud deployment-manager deployments create hierarchy-org-example-prod --template env_demo_project.py --properties=envName:prod
```