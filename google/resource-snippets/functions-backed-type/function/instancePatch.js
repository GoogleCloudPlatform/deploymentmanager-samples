/**
 * This module shows how to use Google API to patch a Cloud SQL instance.
 */

 /**
  * Google API helper, provides a configured ready to use Google API client.
  * See googleApiHelper.js for more information.
  */
 const {getGoogleClient} = require('./googleApiHelper.js');

 /**
  * Patch a Cloud SQL instance:
  * https://cloud.google.com/sql/docs/mysql/admin-api/rest/v1beta4/instances/patch
  */
 exports.instancePatch = async (projectId, instanceId, req) => {
   console.log(`Patching ${instanceId}`);

   const google = await getGoogleClient();
   const patchResult = await google
                             .sqladmin({version: 'v1beta4'})
                             .instances
                             .patch({ project: projectId, instance: instanceId, requestBody: req.body });

   // In this example we're returning just a subset of the response, not the whole object.
   const instance = {
     result: patchResult.statusText,
     instance: instanceId
   }

   return instance;
 }
