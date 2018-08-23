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

### What is the difference?

 
 ```bash
git diff --name-status --no-index ../my_ecom_system/ ./

The real modifications:

# Storing the project related configurations.
R100    ../my_ecom_system/configs/dev/backend.py        ./configs/dev/project.py

A       ./configs/modules/project.py
R100    ../my_ecom_system/configs/prod/backend.py       ./configs/prod/project.py
M       ../my_ecom_system/configs/system_config.py
R100    ../my_ecom_system/configs/test/backend.py       ./configs/test/project.py
D       ../my_ecom_system/env_demo_project.py
A       ./project_creation.py
R065    ../my_ecom_system/env_demo_project.py.schema    ./project_creation.py.schema
A       ./templates/project_creation

git diff --no-index ../my_ecom_system/ ./

```



## WORKING EXAMPLE TODO FIX

```bash
# Allow bulk (glob style) imports
$ gcloud config set deployment_manager/glob_imports True
# Deploy Dev example
$ gcloud deployment-manager deployments create hierarchy-org-project-creation-dev --template project_creation.py --properties=envName:dev
```