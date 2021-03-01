/**
 * This module shows how to use Google API to get a Cloud SQL instance by name.
 */

 /**
  * Google API helper, provides a configured ready to use Google API client.
  * See googleApiHelper.js for more information.
  */
 const {getGoogleClient} = require('./googleApiHelper.js');

 /**
  * Get a SQL instance by id:
  * https://cloud.google.com/sql/docs/mysql/admin-api/rest/v1beta4/instances/get
  */
 exports.instanceGet = async (projectId, instanceId, req) => {
   console.log(`Getting ${instanceId}`);

   const google = await getGoogleClient();
   const sqlInstance = await google
                               .sqladmin({version: 'v1beta4' })
                               .instances
                               .get({ project: projectId, instance: instanceId });

   // In this example we're returning just a subset of instance info, not the whole object.
   const instance = {
     databaseVersion: sqlInstance.data.databaseVersion,
     instance: sqlInstance.data.name
   }

   return instance;
 }
