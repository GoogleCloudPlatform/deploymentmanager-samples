# Sample DM template for GKE and istio.io

Sample DM template that will initialize an **ALPHA** GKE cluster and add [istio.io](https://istio.io)


**NOTE- You must set your default compute service account to include:**

- ```roles/container.admin``` (Container Engine Admin)
- ```Editor``` (on by default)

To set this, navigate to the IAM section of the Cloud Console and find your default GCE/GKE service account in the following form to set that permission:

`projectNumber-compute@developer.gserviceaccount.com`
