config = {
    'project_module': {
        # Change this to your organization ID.
        'organization-id':
        'CHANGE_ME',  #"123456789016",
        # Change the following to your organization's billing account
        'billing-account-name':
        'CHANGE_ME',  # 'billingAccounts/013456-789ABC-DEF123',
        # The apis to enable in the new project.
        # To see the possible APIs, use gcloud CLI: gcloud service-management list
        'apis': [
            'compute.googleapis.com', 'deploymentmanager.googleapis.com',
            'pubsub.googleapis.com', 'storage-component.googleapis.com',
            'monitoring.googleapis.com', 'logging.googleapis.com'
        ],
        # The service accounts you want to create in the project
        'service-accounts': ['my-service-account-1', 'my-service-account-2'],
        'bucket-export-settings': {
            'create-bucket': True
            # If using an already existing bucket, specify this
            # 'bucket': 'Random-testbucket'
        },

        # Makes the service account that Deployment Manager would use
        # in the generated project an admin
        'set-dm-service-account-as-owner':
        True,
        # IAM policy on the new project
        'iam-policy': {
            'bindings': [
                {
                    'role':
                    'roles/owner',
                    'members': [
                        # NOTE: The DM service account that is creating this project will
                        # automatically be added as an owner.
                        # Add any accounts you want to have access
                        #	'serviceAccount:12345678900@cloudservices.gserviceaccount.com',
                        # 	'serviceAccount:12345678901@cloudservices.gserviceaccount.com'
                    ]
                },
                {
                    'role': 'roles/viewer',
                    'members': ['user:iamtester@deployment-manager.net']
                }
            ]
        }
    }
}
