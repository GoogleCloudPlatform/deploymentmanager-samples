/**
 * @fileoverview Utilities to perform Datastore operations.
 */

'use strict';

const Datastore = require('@google-cloud/datastore');
const logging = require('./logging');

// instantiate a Datastore client
const datastore = Datastore();


/**
 * @param {!Object<string>} key - Entity key.
 * @param {!Array<Object>} data - Entity data.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.insertEntity = (key, data) => {
  const entity = {key: key, data: data};
  return datastore.save(entity);
};


/**
 * @param {string} kind - Name of the Datastore kind.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.getEntities = (kind) => {
  const query = datastore.createQuery(kind);
  return datastore.runQuery(query);
};


/**
 * @param {string} kind - Name of the Datastore kind.
 * @param {string} field - Field to filter by.
 * @param {!*} value - Value to filter by.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.getEntitiesWithFilter = (kind, field, value) => {
  const query = datastore.createQuery(kind).filter(field, value);
  return datastore.runQuery(query);
};


/**
 * Retrieve all child entities of a given kind of a parent entity.
 *
 * @param {!Array<string|number>} parentPath - Path to parent entity.
 * @param {string} kind - Name of kind of children entities.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.getChildrenOfEntity = (parentPath, kind) => {
  const parentKey = datastore.key(parentPath);
  const query = datastore.createQuery(kind).hasAncestor(parentKey);
  return datastore.runQuery(query);
};


/**
 * Create and return a new Datastore key from a given path.
 *
 * @param {!(string|Array<string|number>)} path - Path to new entity.
 * @returns {!Object} Newly created entity key.
 */
exports.createEntityKey = (path) => {
  return datastore.key(path);
};


/**
 * Obtain key of an existing Datastore entity.
 *
 * @param {!Object} entity - Entity obtained from Datastore query.
 * @returns {!Object} - Corresponding key for entity.
 */
exports.getEntityKey = (entity) => {
  return entity[datastore.KEY];
};


/**
 * Update a single field in a Datastore entity or add that field if it
 * does not yet exist.
 *
 * @param {!Array<string|number>} entityPath - Ancestor path to entity.
 * @param {string} field - Field to update or add.
 * @param {!*} value - New value for field.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.updateEntityField = (entityPath, field, value) => {
  const entityKey = datastore.key(entityPath);

  return datastore.get(entityKey)
      .then((results) => {
        const entity = results[0];
        if (!entity) {
          return Promise.reject(
              new Error(`No results found for the key ${entityKey}.`));
        }

        entity[field] = value;
        const updatedEntity = {key: entityKey, data: entity};

        return datastore.update(updatedEntity);
      })
      .catch((err) => {
        return Promise.reject(err);
      });
};


/**
 * @param {!Object} key - Key of entity to update.
 * @param {!Object} data - New entity data.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.updateEntity = (key, data) => {
  const entity = {key: key, data: data};
  return datastore.update(entity);
};


/**
 * @param {!Object} key - Key of entity to delete.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.deleteEntity = (key) => {
  return datastore.delete(key);
};


/**
 * Delete children of an entity of a specified Datastore kind.
 *
 * @param {!Array<string|number>} parentPath - Path to parent entity.
 * @param {string} kind - Name of kind of children entities.
 * @returns {Promise<!Object>} - Promise resolves with API response.
 */
exports.deleteChildrenOfEntity = (parentPath, kind) => {
  return new Promise(function(resolve, reject) {
    exports.getChildrenOfEntity(parentPath, kind)
        .then((results) => {
          const children = results[0];
          const childrenKeys = [];
          for (let child of children) {
            let childKey = exports.getEntityKey(child);
            childrenKeys.push(childKey);
          }
          return exports.deleteEntity(childrenKeys);
        })
        .then((response) => {
          resolve(response);
        })
        .catch((err) => {
          reject(err);
        });
  });
};


/**
 * Verify JSON entity has all required fields.
 *
 * @param {!Array<*>} requiredFields
 * @param {!Object<*,*>} object
 * @returns {!Array<*>} Missing fields in object.
 */
exports.findMissingFields = (requiredFields, object) => {
  const missingFields = [];
  for (let field of requiredFields) {
    if (!(field in object)) {
      missingFields.push(field);
    }
  }
  return missingFields;
};
