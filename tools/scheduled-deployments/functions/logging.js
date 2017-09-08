/**
 * @fileoverview Utilities to log entries for Scheduled Deployments.
 */

'use strict';

const constants = require('./constants');
const datastore = require('./datastore');
const uuid = require('uuid');


/**
 * Log an operation resource in Datastore and the Cloud Functions log.
 *
 * @param {number} parentId - Datastore ID of Scheduled Deployment.
 * @param {string} deploymentName - Name of Scheduled Deployment.
 * @param {Object=} err - Error message if unsuccessful.
 * @param {Object=} response - Response object if successful.
 * @param {string=} prefix - If provided, prepends string to operation name.
 */
exports
    .logOperation = (parentId, deploymentName, err, response, prefix = '') => {
  // set up operation
  const operationPath = [constants.KIND, parentId, constants.OPERATION_KIND];
  const operationKey = datastore.createEntityKey(operationPath);
  const operation = {
    'name': prefix + uuid(),
    'target': deploymentName,
    'done': true
  };

  if (err) {
    operation.error = {
      'message': err.message,
      'timestamp': (new Date()).toISOString()
    };
  } else {
    operation.response = {
      'dmOperationId': response.name,
      'action': response.operationType,
      'timestamp': response.insertTime
    };

    // record timestamp for the Scheduled Deployment action
    const entityPath = [constants.KIND, parentId];
    const timestamp = (new Date(response.insertTime)).toString();
    datastore.updateEntityField(entityPath, 'lastDeployed', timestamp)
        .catch((err) => {
          logging.logError(
              `Unable to update 'lastDeployed' field for Scheduled ` +
                  `Deployment '${deploymentName}'.`,
              err);
        });
  }

  // log in Datastore
  const operationData = [];
  for (let key in operation) {
    const property = {name: key, value: operation[key]};
    operationData.push(property);
  }
  datastore.insertEntity(operationKey, operationData)
      .then(() => {
        // log in Cloud Functions logs
        if ('error' in operation) {
          exports.logWithJson(
              'Scheduled Deployment unsuccessful. The operation is:',
              operation);
        } else {
          exports.logWithJson(
              'Scheduled Deployment successful. The operation is:', operation);
        }
      })
      .catch((err) => {
        logging.logError('Unable to put Operation entity in Datastore.', err);
      });
};


/**
 * Create a log entry with a message and corresponding JSON content.
 *
 * @param {string} message - Message to log.
 * @param {!Object} json - JSON object with content to embed in log entry.
 */
exports.logWithJson = (message, json) => {
  exports.logMessage(message + '\n' + JSON.stringify(json, null, 2));
};


/**
 * Create a log entry with an error message and corresponding JSON content.
 *
 * @param {string} message - Error message to log.
 * @param {!Object} json - JSON object with content to embed in log entry.
 */
exports.logErrorWithJson = (message, json) => {
  exports.logError(message + '\n' + JSON.stringify(json, null, 2));
};


/**
 * Create a log entry with a provided message.
 *
 * @param {string} message - Message to log.
 */
exports.logMessage = (message) => {
  console.log(message);
};


/**
 * Create a log entry with an error message.
 *
 * @param {string} message - Error message to log.
 * @param {Error=} err - Optional error message.
 */
exports.logError = (message, err = '') => {
  console.error('ERROR: ' + message, err);
};
