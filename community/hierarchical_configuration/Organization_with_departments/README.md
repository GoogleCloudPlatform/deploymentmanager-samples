# Extended Hierarchical structure for Deployment Manager configuration

## Summary
This example is an extension of the "basic" Hierarchical structure.

Compare to the "basic" version, this example handles a more complex Organization hierarchy where Org and Department level configs,
 helper functions and templates can be shared. It also supports the concept of muliple Systems (IT Projects).
 
 
 ### System setup
 
 Note: In this example we define 'System': as a logical unit of Cloud environment, like an e-commerce platform. 
 (Trying to avoid using the word 'Project' to avoid confusion with GCP projects)
 
 The following Symbolic links are putting the appropriate global configurations to the right path:
 
 ```bash
 ln -sf ../../../global/helper/config_merger.py helper/config_merger.py
 ln -sf ../../../global/helper/naming_helper.py helper/naming_helper.py
 ln -sf ../../../global/configs/org_config.py configs/org_config.py

```
 
 # Select the appropriate department from the Global list:
 ```bash
 ln -sf ../../../global/configs/Department_Data_config.py configs/department_config.py
```

## WORKING EXAMPLE

```bash

# These 5 commands will get you up and running! This will deploy Dev,Test, Prod env as specified in the CLI argument
$ git clone https://github.com/GoogleCloudPlatform/deploymentmanager-samples.git
$ cd deploymentmanager-samples/community/hierarchical_configuration/Organization_with_departments/systems/my_ecom_system
# set project_id <your-personal-project-id> # (or add it to next gcloud commands)
# Allow bulk (glob style) imports
$ gcloud config set deployment_manager/glob_imports True
# Deploy Dev example
$ gcloud deployment-manager deployments create hierarchy-org-example-dev --template env_demo_project.py --properties=envName:dev
# Deploy Test example
$ gcloud deployment-manager deployments create hierarchy-org-example-test --template env_demo_project.py --properties=envName:test
# Deploy Prod example
$ gcloud deployment-manager deployments create hierarchy-org-example-prod --template env_demo_project.py --properties=envName:prod
```