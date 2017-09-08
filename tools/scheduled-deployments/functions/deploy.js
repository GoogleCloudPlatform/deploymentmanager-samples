/**
 * @fileoverview Helper functions that implement the Deployment stage of
 * Scheduled Deployments.
 */

'use strict';

const async = require('async');
const cronParser = require('cron-parser');
const google = require('googleapis');
const uuid = require('uuid/v1');
const yamljs = require('yamljs');
const constants = require('./constants');
const datastore = require('./datastore');
const logging = require('./logging');
const schedule = require('./schedule');

const deploymentManager = google.deploymentmanager('v2');


/**
 * Deploy specified configuration.
 *
 * @param {!Object} deploymentDetails - Details from Datastore entity.
 * @param {string} deploymentName
 * @param {number} parentId - Entity ID of the Scheduled Deployment parent.
 * @param {string=} prefix - If provided, prepends string to deployment name.
 */
exports
    .deployConfig = (deploymentDetails, deploymentName, parentId, prefix = '') => {
  const requiredFields = ['config', 'description'];
  const missingFields =
      datastore.findMissingFields(requiredFields, deploymentDetails);
  if (missingFields.length > 0) {
    throw new Error(
        'Datastore trigger entity missing the following fields: ' +
        missingFields.join(','));
  }

  exports.authorize()
      .then((authClient) => {
        const request = {
          project: constants.PROJECT_ID,
          resource: {
            'name': prefix + deploymentName,
            'description': deploymentDetails.description,
            'target': {
              'config':
                  {'content': yamljs.stringify(deploymentDetails.config, 2)}
            }
          },
          auth: authClient
        };

        // not all configurations will have imports
        if ('importName' in deploymentDetails &&
            'importContent' in deploymentDetails) {
          request.resource.target.imports = [{
            'name': deploymentDetails.importName,
            'content': deploymentDetails.importContent
          }];
        } else if (
            'importName' in deploymentDetails ||
            'importContent' in deploymentDetails) {
          throw new Error(
              `Trigger entity from Datastore missing one of 'importName' ` +
              `or 'importContent'.`);
        }

        deploymentManager.deployments.insert(request, function(err, response) {
          logging.logOperation(parentId, deploymentName, err, response, prefix);
        });
      })
      .catch((err) => {
        logging.logError(
            `Unable to deploy Scheduled Deployment '${deploymentName}'.`, err);
      });
};


/**
 * Delete specified deployment.
 *
 * @param {string} deploymentName - Name of deployment to delete.
 * @param {number} parentId - Entity ID of the Scheduled Deployment parent.
 * @param {string=} prefix - If provided, prepends string to deployment name.
 */
exports.deleteDeployment = (deploymentName, parentId, prefix = '') => {
  exports.authorize()
      .then((authClient) => {
        const request = {
          project: constants.PROJECT_ID,
          deployment: prefix + deploymentName,
          auth: authClient
        };
        deploymentManager.deployments.delete(request, function(err, response) {
          logging.logOperation(parentId, deploymentName, err, response, prefix);
        });
      })
      .catch((err) => {
        logging.logError(
            `Unable to delete Scheduled Deployment '${deploymentName}'. ` +
                'Deployment Manager authentication failed.\n',
            err);
      });
};


/**
 * Retrieve Trigger entities in Datastore linked to the provided Scheduled
 * Deployment entity and send those Triggers to be checked.
 *
 * @param {!Object} scheduledDeployment - Entity from Datastore.
 * @returns {Promise<!Array<!Object>>} Trigger entities corresponding to the
 *     provided Scheduled Deployment.
 */
exports.getTriggers = (scheduledDeployment) => {
  const deploymentPath = datastore.getEntityKey(scheduledDeployment).path;

  return new Promise(function(resolve, reject) {
    datastore.getChildrenOfEntity(deploymentPath, constants.TRIGGER_KIND)
        .then((results) => {
          const triggers = results[0];
          resolve(triggers);
        })
        .catch((err) => {
          reject(err);
        });
  });
};


/**
 * Iterate through Trigger entries from Datastore and make an array of all
 * active triggers.
 *
 * @param {!Array<!Object>} triggers - Trigger entities from Datastore.
 * @param {!Object} parent - Scheduled Deployment entity.
 * @returns {Promise<!Array<!Object>>} Promise resolves to an array of all
 *     active Trigger entities.
 */
exports.getActiveTriggers = (triggers, parent) => {
  const deploymentName = parent.name;
  const lastDeployed = parent.lastDeployed || 0;

  return new Promise((resolve, reject) => {
    const activeTriggers = [];
    const currentTime = Date.now();
    async.forEachOf(
        triggers,
        (trigger, _, callback) => {
          schedule.isTriggerFormatValid(trigger, deploymentName)
              .then(() => {
                const crontab = trigger.time;
                return exports.crontabWithinInterval(
                    currentTime, constants.CRON_INTERVAL_IN_MIN, crontab,
                    lastDeployed);
              })
              .then((timestamp) => {
                if (timestamp > 0) {
                  activeTriggers.push({timestamp: timestamp, entity: trigger});
                }
                callback();
              })
              .catch((err) => {
                return callback(err);
              });
        },
        (err) => {
          if (err) {
            reject(err);
          } else {
            resolve(activeTriggers);
          }
        });
  });
};


/**
 * Select the active trigger with the latest timestamp and make a deployment
 * or deletion as appropriate.
 *
 * @param {!Array<!Object>} activeTriggers - List of active triggers.
 * @param {!Object} parent - Scheduled Deployment entity.
 */
exports.processActiveTriggers = (activeTriggers, parent) => {
  const deploymentName = parent.name;
  const parentId = parseInt(datastore.getEntityKey(parent).id);
  if (activeTriggers.length > 0) {
    const latestTrigger = activeTriggers.sort(exports.compareTriggers)[0];
    if (latestTrigger.entity.action == 'CREATE_OR_UPDATE') {
      exports.deployConfig(
          latestTrigger.entity, deploymentName, parentId, constants.PREFIX);
    } else if (latestTrigger.entity.action == 'DELETE') {
      exports.deleteDeployment(deploymentName, parentId, constants.PREFIX);
    } else {
      loggging.logError(
          `Unknown trigger action ${latestTrigger.entity.action}.`);
    }
  }
};

/**
 * Comparison function to sort trigger entities. Priority goes first to later
 * timestamps and second in reverse alphabetical order of name.
 *
 * @param {{timestamp: number, entity: {name: string}}} x - Trigger object.
 * @param {{timestamp: number, entity: {name: string}}} y - Trigger object.
 * @returns {number} -1 if x has priority
 *                    1 if y has priority
 *                    0 if neither has priority over the other
 */
exports.compareTriggers = (x, y) => {
  if (x.timestamp > y.timestamp) {
    return -1;
  } else if (x.timestamp < y.timestamp) {
    return 1;
  } else if (x.entity.name > y.entity.name) {
    return -1;
  } else if (x.entity.name < y.entity.name) {
    return 1;
  } else {
    return 0;
  }
};


/**
 * Determine whether the provided time falls within the current interval of
 * the crontab schedule. If so, return the time scheduled for the deployment.
 *
 * A time is considered within the interval if it's within interval/2 minutes
 * before or after the Cron trigger.
 *
 * @param {number} time - current time in UNIX epoch time (milliseconds)
 * @param {number} interval - time between Cron timer events (minutes)
 * @param {string} crontab - time of trigger, in crontab format
 * @param {number} lastDeployed - last time this scheduled deployment was
 *     deployed, in UNIX epoch time (milliseconds)
 * @returns {Promise<number>} time in UNIX epoch of the scheduled time if
 *     valid; 0 otherwise
 */
exports.crontabWithinInterval = (time, interval, crontab, lastDeployed) => {
  return new Promise((resolve, reject) => {
    const schedule = cronParser.parseExpression(crontab, {currentDate: time});
    const prevScheduled = schedule.prev().getTime();
    const nextScheduled = schedule.next().getTime();

    if (nextScheduled <= (time + ((interval / 2) * 1000 * 60))) {
      resolve(nextScheduled);
    } else if (prevScheduled >= (time - ((interval / 2) * 1000 * 60))) {
      resolve(prevScheduled);
    } else if (lastDeployed < prevScheduled) {
      // we missed the most recent deployment
      resolve(prevScheduled);
    } else {
      resolve(0);
    }
  });

};


/**
 * Authorize client to access Deployment Manager.
 *
 * @returns {Promise<AuthClient>} Authorization credential for use in calling
 *     Google APIs.
 */
exports.authorize = () => {
  return new Promise((resolve, reject) => {
    google.auth.getApplicationDefault((err, authClient) => {
      if (err) {
        reject(err);
      }
      if (authClient.createScopedRequired &&
          authClient.createScopedRequired()) {
        const scopes = ['https://www.googleapis.com/auth/cloud-platform'];
        authClient = authClient.createScoped(scopes);
      }
      resolve(authClient);
    });
  });
};
