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
A simple project name generator helper class is added which defines and enforces the project naming convention.
This helper class can be called from inside the project creator template. In this case it's enforced in the template level.
Alternatively it can be called at the main template where the apropriate project-name and/or project-id parameter can be overwritten.