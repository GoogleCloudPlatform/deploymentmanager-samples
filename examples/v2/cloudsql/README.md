# CloudSQL Testing Framework

## Introduction 

This package contains Google Cloud DeploymentManager templates to automate the deployment of CloudSQL clusters, along with clients that access them. Currently, the only client is [cloud_sql_proxy](https://cloud.google.com/sql/docs/mysql/sql-proxy) running on CentOS 7.

## Deployment

One can reference the templates [schema files](https://cloud.google.com/deployment-manager/docs/configuration/templates/using-schemas) for a description of availble options.

**NOTE:** This procedure assumes gcloud is installed

	## Copy example config files. 
	$ cp db.example.yaml db.yaml
	$ cp client.example.yaml client.yaml


	## Update db.yaml accordingly. See running example below
	$ cat db.yaml
	imports:
	  - path: cloudsql.jinja

	resources:
	  - name: cloudsql
	    type: cloudsql.jinja
	    properties:
	      database:
            name: test
	      dbUser: 
	        password: test123_
	      failover: true
	      readReplicas: 1


	$ gcloud deployment-manager deployments create db01 --config db.yaml
	... 
    
	## Get Outputs
	$ gcloud deployment-manager manifests describe --deployment db01 | sed -n 's@^.*finalValue: @@p'1 
	35.193.165.42
	go-bears:us-central1:db01-cloudsql-master
	35.202.14.154
	go-bears:us-central1:db01-cloudsql-failover
	35.224.104.137
	go-bears:us-central1:db01-cloudsql-rr-0

	## Use the connection string(s) accordingly (See https://cloud.google.com/sql/docs/mysql/sql-proxy](). CloudSQL Proxy will use this string accordinly. 
	$ cat client.yaml
	imports:
	  - path: cloudsql_client.jinja
	  - path: scripts/cloud-sql-proxy.sh
	    name: startup-script

	resources:
	  - name: client
	    type: cloudsql_client.jinja
	    properties:
	      cloud-sql-instances: go-bears:us-central1:db01-cloudsql-master
	      clientCount: 2

	$ gcloud deployment-manager deployments create client01 --config client.yaml
	... 

	## Ssh into an instance and test mysql 
	[mwallman@client01-client-0 ~]$ mysql -uroot -S /var/cloudsql/go-bears\:us-central1\:db01-cloudsql-master -ptest123_ test
	
	...
	MySQL [test]>
