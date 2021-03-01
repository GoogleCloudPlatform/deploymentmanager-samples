/**
 * Google API Javascript library:
 *   * https://github.com/googleapis/google-api-nodejs-client
 *
 * Sqladmin Instances API:
 *   * https://googleapis.dev/nodejs/googleapis/latest/sqladmin/classes/Sqladmin.html
 *   * https://cloud.google.com/sql/docs/mysql/admin-api/rest/v1beta4/instances
 *
 *
 * Note. Must be included as dependency in package.json.
 */

const {google} = require('googleapis');

/**
 * Auth scopes for different services:
 * https://developers.google.com/identity/protocols/oauth2/scopes#sqladmin
 */
const sqlScopes = [
  'https://www.googleapis.com/auth/cloud-platform',
  'https://www.googleapis.com/auth/sqlservice.admin'
];

/**
 * Returns a configured ready to use Google API client.
 */
exports.getGoogleClient = async () => {
  const authClient = await google.auth.getClient({ scopes: sqlScopes });
  google.options({auth: authClient});
  return google;
}
