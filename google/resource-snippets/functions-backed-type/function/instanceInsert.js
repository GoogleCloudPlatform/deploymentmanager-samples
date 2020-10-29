/**
 * This module shows how to use Google API to insert a Cloud SQL instance.
 */

 /**
  * Google API helper, provides a configured ready to use Google API client.
  * See googleApiHelper.js for more information.
  */
 const {getGoogleClient} = require('./googleApiHelper.js');

 /**
  * Insert a Cloud SQL instance:
  * https://cloud.google.com/sql/docs/mysql/admin-api/rest/v1beta4/instances/insert
  */
 exports.instanceInsert = async (projectId, instanceId, req) => {
   console.log(`Inserting ${instanceId}`);

   const google = await getGoogleClient();
   const insertResult = await google
                         .sqladmin({version: 'v1beta4'})
                         .instances
                         .insert({ project: projectId, requestBody: req.body });

   // In this example we're returning just a subset of result, not the whole object.
   const instance = {
     result: insertResult.statusText,
     instance: instanceId
   }

   return instance;
 }

