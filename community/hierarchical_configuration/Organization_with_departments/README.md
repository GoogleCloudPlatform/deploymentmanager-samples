# Extended Hierarchical structure for Deployment Manager configuration

## Summary
This example is an extension of the "basic" Hierarchical structure.

Compare to the "basic" version, this example handles a more complex Organization hierarchy where Org and Department level configs,
 helper functions and templates can be shared. It also supports the concept of muliple Systems (IT Projects).
 
 
 ### Project setup
 
 The following Symbolic links are putting the appropriate global configurations to the right path:
 ln -sf ../../../global/helper/config_merger.py helper/config_merger.py
 ln -sf ../../../global/configs/org_config.py configs/org_config.py
 
 # Select the appropriate department from the Global list:
 ln -sf ../../../global/configs/Department_Data_config.py configs/department_config.py