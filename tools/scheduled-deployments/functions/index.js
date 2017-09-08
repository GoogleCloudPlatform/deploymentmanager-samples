/**
 * @fileoverview Define Cloud Functions that execute stages of the
 * Scheduled Deployments workflow.
 */

'use strict';

const async = require('async');
const constants = require('./constants');
const datastore = require('./datastore');
const deploy = require('./deploy');
const logging = require('./logging');
const schedule = require('./schedule');


/**
 * Create, read, update, or delete a Scheduled Deployment entity in Datastore
 * according to details from a JSON payload.
 *
 * @param {!Object} req - HTTP request context.
 * @param {!Object} res - HTTP response context.
 */
exports.router = (req, res) => {
  const name = schedule.parseNameFromUrl(req.url, req.method);
  const data = req.body;

  if (req.method === 'POST') {
    schedule.create(name, data, res);
  } else {
    datastore.getEntitiesWithFilter(constants.KIND, 'name', name)
        .then((results) => {
          const entities = results[0];
          if (entities.length === 0) {
            res.status(404).send(
                `No Scheduled Deployments found with name '${name}'.`);
            return;
          } else if (entities.length > 1) {
            res.status(409).send(
                `More than one Scheduled Deployment found with name '${
                                                                       name
                                                                     }'.`);
            return;
          }

          const entity = entities[0];
          switch (req.method) {
            case 'GET':
              schedule.read(name, entity, res);
              return new Promise.resolve('yay');
              break;
            case 'PUT':
              schedule.update(name, entity, data, res);
              break;
            case 'DELETE':
              schedule.delete(name, entity, res);
              break;
            default:
              res.status(405).send(
                  {error: `Undefined request type ${req.method}.`});
          }
        })
        .catch((err) => {
          res.status(500).send(
            {error: `Unable to retrieve Scheduled Deployment '${name}'.` + err.message});
        });
  }
};


/**
 * Check Scheduled Deployment entities in Datastore and make all necessary
 * deployments using Deployment Manager.
 *
 * @param {!Object} event - Event from Pub/Sub trigger.
 * @param {!function(?Error=, *=)} callback - Callback function.
 */
exports.deployScheduledDeployments = (event, callback) => {
  logging.logMessage('Checking for Scheduled Deployments to deploy.');

  datastore.getEntities(constants.KIND)
      .then((results) => {
        const scheduledDeployments = results[0];

        if (scheduledDeployments.length === 0) {
          logging.logMessage(
              'No Scheduled Deployments entries found in Datastore.');
          callback();
          return;
        }

        async.forEachOf(
            scheduledDeployments,
            (scheduledDeployment, _, asyncCallback) => {
              deploy.getTriggers(scheduledDeployment)
                  .then((triggers) => {
                    return deploy.getActiveTriggers(
                        triggers, scheduledDeployment);
                  })
                  .then((activeTriggers) => {
                    deploy.processActiveTriggers(
                        activeTriggers, scheduledDeployment);
                    asyncCallback();
                  })
                  .catch((err) => {
                    return asyncCallback(err);
                    logging.logError(
                        `Unable to retrieve Trigger entities for Scheduled ` +
                            `Deployment ${scheduledDeployment.name}.`,
                        err);
                  });
            },
            (err) => {
              if (err) {
                throw err;
              } else {
                callback();
              }
            });
      })
      .catch((err) => {
        throw new Error(
            'Unable to retrieve Scheduled Deployment entities.', err);
      });
};
