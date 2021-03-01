/**
 * This module shows how to use Google API to delete a Cloud SQL instance by name.
 */

/**
 * Google API helper, provides a configured ready to use Google API client.
 * See googleApiHelper.js for more information.
 */
const {getGoogleClient} = require('./googleApiHelper.js');

/**
 * Delete a SQL instance by id:
 * https://cloud.google.com/sql/docs/mysql/admin-api/rest/v1beta4/instances/get
 */
exports.instanceDelete = async (projectId, instanceId, req) => {
  console.log(`Deleting ${instanceId}`);

  const google = await getGoogleClient();
  const deleteResult = await google
                                .sqladmin({version: 'v1beta4' })
                                .instances
                                .delete({ project: projectId, instance: instanceId });
  return {
    instance: instanceId,
    result: deleteResult.statusText,
  }
}
