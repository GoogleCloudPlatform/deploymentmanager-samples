/**
 * @fileoverview Helper functions to implement the Scheduling stage of
 * Scheduled Deployments.
 */

'use strict';

const base64 = require('js-base64');
const constants = require('./constants');
const datastore = require('./datastore');
const logging = require('./logging');


/**
 * Extract details of a Scheduled Deployment from a JSON payload and
 * record details as a new Datastore entity.
 *
 * @param {string} name - Name of the Scheduled Deployment to create.
 * @param {!Object} deploymentDetails - Deployment details from HTTP request.
 * @param {!Object} res - HTTP response context.
 */
exports.create = (name, deploymentDetails, res) => {
  // validate format of JSON payload
  const requiredFields = ['user', 'description', 'triggers'];
  const missingFields =
      datastore.findMissingFields(requiredFields, deploymentDetails);
  if (missingFields.length > 0) {
    res.status(400).send(
        'Missing required fields in Scheduled Deployment config: ' +
        missingFields.join());
    return;
  }
  if (!Array.isArray(deploymentDetails.triggers)) {
    res.status(400).send(
        'Scheduled Deployment triggers must be input as an array.');
    return;
  }
  if (deploymentDetails.triggers.length === 0) {
    res.status(400).send(
        'A Scheduled Deployment must have at least one trigger.');
    return;
  }

  const parentKey = datastore.createEntityKey(constants.KIND);
  const parentData = [
    {name: 'name', value: name},
    {name: 'description', value: deploymentDetails.description},
    {name: 'user', value: deploymentDetails.user},
    {name: 'submitted', value: new Date()}
  ];

  // ensure no entity exists in Datastore with the same name
  exports.enforceUniqueDeploymentName(name)
      .then(() => {
        return datastore.insertEntity(parentKey, parentData);
      })
      .then(() => {
        return exports.putTriggerEntities(
            name, parentKey, deploymentDetails.triggers);
      })
      .then(() => {
        logging.logMessage(`Recorded the Scheduled Deployment '${name}'.`);
        res.status(200).end(`Recorded the Scheduled Deployment '${name}'.`);
      })
      .catch((err) => {
        logging.logError(
            `Unable to record Scheduled Deployment '${name}'.`, err);
        res.status(400).end(`Unable to record Scheduled Deployment '${name}'.`);
      });
};


/**
 * Return details of a Scheduled Deployment in the HTTP response.
 *
 * @param {string} name - Name of the Scheduled Deployment.
 * @param {!Object} entity - Scheduled Deployment entity from Datastore.
 * @param {!Object} res - HTTP response context.
 */
exports.read = (name, entity, res) => {
  logging.logWithJson(`The Scheduled Deployment ${name} is `, entity);
  res.json(entity);
  res.status(200).json();
};


/**
 * Update a Scheduled Deployment by inserting the new deployment details.
 *
 * @param {string} name - Name of the Scheduled Deployment.
 * @param {!Object} entity - Scheduled Deployment entity from Datastore.
 * @param {!Object} deploymentDetails - Deployment details from HTTP request.
 * @param {!Object} res - HTTP response context.
 */
exports.update = (name, entity, deploymentDetails, res) => {
  // delete existing Trigger entities
  const parentKey = datastore.getEntityKey(entity);
  datastore.deleteChildrenOfEntity(parentKey.path, constants.TRIGGER_KIND)
      .then(() => {
        // update Scheduled Deployment entity
        const data = [
          {name: 'name', value: name},
          {name: 'description', value: deploymentDetails.description},
          {name: 'user', value: deploymentDetails.user},
          {name: 'submitted', value: new Date()}
        ];
        return datastore.updateEntity(parentKey, data);
      })
      .then(() => {
        // insert new Trigger entities
        exports.putTriggerEntities(name, parentKey, deploymentDetails.triggers);

        logging.logMessage(`Updated the Scheduled Deployment '${name}'.`);
        res.status(200).end();
      })
      .catch((err) => {
        logging.logError(
            `Unable to update Scheduled Deployment '${name}'. `, err);
        res.status(500).end();
      });
};


/**
 * Delete a Scheduled Deployment by removing its details from Datastore.
 *
 * @param {string} name - Name of the Scheduled Deployment.
 * @param {!Object} entity - Scheduled Deployment entity from Datastore.
 * @param {!Object} res - HTTP response context.
 */
exports.delete = (name, entity, res) => {
  const key = datastore.getEntityKey(entity);

  // delete corresponding triggers and operations
  datastore.deleteChildrenOfEntity(key.path, constants.TRIGGER_KIND);
  datastore.deleteChildrenOfEntity(key.path, constants.OPERATION_KIND);

  datastore.deleteEntity(key)
      .then((data) => {
        logging.logMessage(`Deleted the Scheduled Deployment '${name}'.`);
        const apiResponse = data[0];
        res.json(apiResponse);
        res.status(200).end();
      })
      .catch((err) => {
        logging.logError(
            `Unable to delete Scheduled Deployment '${name}'.`, err);
        res.status(500).end();
        return;
      });
};



/**
 * Ensure the name of a new Scheduled Deployment does not conflict with
 * any existing entities in Datastore.
 *
 * @param {string} name - Proposed Scheduled Deployment name.
 * @returns {Promise<null>}
 */
exports.enforceUniqueDeploymentName = (name) => {
  return new Promise(function(resolve, reject) {
    datastore.getEntitiesWithFilter(constants.KIND, 'name', name)
        .then((results) => {
          if (results[0].length > 0) {
            reject(`A Scheduled Deployment already exists with the name '${
                                                                           name
                                                                         }'.`);
          }
          resolve();
        })
        .catch((err) => {
          reject(err);
        });
  });
};


/**
 * Extract details of a Scheduled Deployment trigger from a JSON payload
 * and record details as a new Datastore entity.
 *
 * @param {string} parentName - Name of Scheduled Deployment parent.
 * @param {{kind: string, id: number}} parentKey - Identifiers of the parent
 *     entity in Datastore.
 * @param {!Array<!Object>} triggers - Trigger entities from Datastore.
 * @returns {Promise<null>}
 */
exports.putTriggerEntities = (parentName, parentKey, triggers) => {
  return new Promise(function(resolve, reject) {
    for (let trigger of triggers) {
      exports.isTriggerFormatValid(trigger, parentName)
          .then(() => {
            const triggerPath =
                [parentKey.kind, parentKey.id, constants.TRIGGER_KIND];
            const triggerKey = datastore.createEntityKey(triggerPath);
            const triggerData = [
              {name: 'name', value: trigger.name},
              {name: 'type', value: trigger.type},
              {name: 'time', value: trigger.time},
              {name: 'action', value: trigger.action},
              {name: 'description', value: trigger.description},
              {name: 'submitted', value: (new Date()).toISOString()}
            ];

            if (trigger['action'] === 'CREATE_OR_UPDATE') {
              // these fields are not necessary for DELETE
              triggerData.push({name: 'config', value: trigger.config});
              if ('importName' in trigger && 'importContent' in trigger) {
                triggerData.push(
                    {name: 'importName', value: trigger.importName});
                triggerData.push(
                    {name: 'importContent', value: trigger.importContent});
              } else if (
                  'importName' in trigger || 'importContent' in trigger) {
                reject(new Error(
                    `Both 'importName' and 'importContent' are required to ` +
                    'import a template in a configuration.'));
              }
            }

            datastore.insertEntity(triggerKey, triggerData).catch((err) => {
              reject(err);
            });
          })
          .catch((err) => {
            reject(err);
          });
    }
    resolve();
  });
};


/**
 * Ensure a Trigger entity in Datastore has the correct format.
 *
 * @param {!Object<string>} trigger - Entity from Datastore.
 * @param {string} parentName - Name of Scheduled Deployment parent.
 * @returns {Promise<boolean>} Whether entity has the correct format.
 */
exports.isTriggerFormatValid = (trigger, parentName) => {
  return new Promise((resolve, reject) => {
    const requiredFields = ['action', 'name', 'type', 'time'];
    const missingFields = datastore.findMissingFields(requiredFields, trigger);
    if (missingFields.length > 0) {
      if ('name' in missingFields) {
        reject(new Error(
            'Missing required fields in Trigger entity of Scheduled ' +
            `Deployment ${parentName}': ` + missingFields.join()));
      } else {
        reject(new Error(
            `Missing required fields in Trigger entity '${trigger.name}' of` +
            `Scheduled Deployment '${parentName}': ` + missingFields.join()));
      }
    }
    if (trigger.action != 'DELETE' && trigger.action != 'CREATE_OR_UPDATE') {
      reject(new Error(
          'Trigger action must be either CREATE_OR_UPDATE or DELETE.'));
    }
    resolve(true);
  });
};


/**
 * Extract Scheduled Deployment name from provided URL path or query. The name
 * is provided as a query (?name=...) in the POST method and as a path (/...)
 * otherwise.
 *
 * @param {string} url - URL fragment of request as query or path.
 * @param {string} method - HTTP request method.
 * @returns {string} Name from URL fragment.
 */
exports.parseNameFromUrl = (url, method) => {
  if (method == 'POST') {
    const parsed = url.split('=');
    return parsed.slice(-1)[0];
  } else {
    return url.substr(1);
  }
};
