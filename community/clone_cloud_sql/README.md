## Description

[Clone](https://cloud.google.com/sql/docs/mysql/admin-api/v1beta4/instances/clone)
an existing [Cloud SQL](https://cloud.google.com/sql/) instance and optionally
acquire it into the deployment.

## Notes
  - Cloud SQL tends to return 403 when something can't be found, so if you see
    an error like:

    ```
    "ResourceErrorCode": 403, "message": "The client is not authorized to make
    this request.", "requestPath": "https://...
    ```

    Then ensure that the Instance in the requestPath actually exists and that
    the [authority that Deployment Manager uses](https://cloud.google.com/deployment-manager/docs/access-control#access_control_for_deployment_manager)
    has permissions on it.

  - If the new Instance's name is already taken, then you will receive an error
    like:

    ```
    "ResourceErrorCode": "409", "message": "The Cloud SQL instance already
    exists."
    ```

    Note that  Cloud SQL Instance names are reserved for a week after instance
    deletion, see https://cloud.google.com/sql/docs/mysql/delete-instance.

