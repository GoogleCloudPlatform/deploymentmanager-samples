This template creates a pool of VMs in a given zone. The VM properties, zone,
and the pool size are captured as properties of the template and can be
configured by the user. The template has a schema defined in
instance-pool.py.schema

To create a deployment of this template run

`$ gcloud deployment-manager deployments create instance-pool --config instance-pool.yaml`
