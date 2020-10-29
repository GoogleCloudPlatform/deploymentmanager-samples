/**
 * This function calls Sqladmin APIs to manage a Cloud SQL instance.
 *
 * CRUD operations for SQL instances are split out into their own files.
 * See those files for examples of how to call the specific APIs.
 * See googleApiHelper.js for information about how to use the Google API client.
 */

/**
 * GCP_PROJECT runtime env variable needs to be manually set during
 * function deployment if using Node10+ runtime, see:
 * https://cloud.google.com/functions/docs/env-var#environment_variables_set_automatically
 */
const currentProject = process.env.GCP_PROJECT;

/**
 * Cloud SQL CRUD operations are implemented in corresponding files and are mapped to HTTP verbs.
 */
const sqlMethods = {
  "GET": require('./instanceGet.js').instanceGet,
  "POST": require('./instanceInsert.js').instanceInsert,
  "PUT": require('./instancePatch.js').instancePatch,
  "DELETE": require('./instanceDelete.js').instanceDelete
}

/**
 * Entry point.
 */
exports.getSqlInstanceByName = async (req, res) => {
  try {
    logRequestInfo(req);

    if (!(req.method in sqlMethods)) {
      throw { code: 400, error: { message: `Unsupported method: ${req.method}` } };
    }

    const instanceId = parseInstanceId(req);

    // Call the Google API corresponding to the HTTP verb
    const result = await sqlMethods[req.method](currentProject, instanceId, req);

    console.log(`${req.method} finished. Result: ${JSON.stringify(result)}`);
    res.status(200).send(result);
  } catch(err) {
    handleError(req, res, err);
  }
}

/**
 * Catch and log errors, return a simplified error object according to the API descriptor.
 */
function handleError(req, res, err) {
  console.log(`${req.method} error: ${JSON.stringify(err)}`);
  if (err.errors && err.errors.length > 0) {
    const code = (err.code && parseInt(err.code)) || 400;
    res.status(code).send({ code: code, error: { message: JSON.stringify(err.errors) }});
  } else {
    res.status(500).send({ code: 500, error: { message: `Unknown error getting a SQL instance. ${JSON.stringify(err)}` } });
  }
}

/**
 * Logging request information verbatim.
 * For demostration and debugging purposes.
 * Be careful not to log any sensitive information accidentally.
 */
function logRequestInfo(req) {
  console.log(`Request method: ${req.method}. Body: ${JSON.stringify(req.body)}`);
  console.log(`Request path: ${JSON.stringify(req.path)}`);
  console.log(`Request query: ${JSON.stringify(req.query)}`);
  console.log(`Request params: ${JSON.stringify(req.params)}`);
}

/**
 * Extract SQL instance id from URL path.
 * This is according to the API descriptor document used for the type provider.
 */
function parseInstanceId(req) {
  const paramKeys = Object.keys(req.params);

  if (paramKeys.length != 1 || !req.params[paramKeys[0]]) {
    throw { code: 400, error: { message: 'Instance id not specified in the URL.' } };
  }

  return req.params[paramKeys[0]]
}
