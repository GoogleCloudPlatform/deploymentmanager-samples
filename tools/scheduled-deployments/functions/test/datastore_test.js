'use strict';

const assert = require('chai').assert;
const expect = require('chai').expect;
const sinon = require('sinon');
const datastore = require('../datastore');
const DatastoreAPI = require('@google-cloud/datastore');

const sandbox = sinon.createSandbox();


describe('datastore.insertEntity()', function() {
  const key = {id: 10, name: 'mango'};
  const data = {name: 'deployment', triggers: [{}, {}, {}]};
  let saveStub;

  beforeEach(function() {
    saveStub = sandbox.stub(DatastoreAPI.prototype, 'save');
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('inserts successfully', function() {
    saveStub.returns('Saved!');
    assert.equal(datastore.insertEntity(key, data), 'Saved!');
    const entity = {key: key, data: data};
    assert(saveStub.calledOnce);
    assert(saveStub.calledWith(entity));
  });
  it('throws error if insert fails', function() {
    const error = new Error('Uh oh!');
    saveStub.throws(error);
    assert.throws(function() {
      datastore.insertEntity(key, data);
    }, error);
  });
});

describe('datastore.getEntities()', function() {
  const kind = 'Berries';
  let createQueryStub;
  let runQueryStub;

  beforeEach(function() {
    createQueryStub = sandbox.stub(DatastoreAPI.prototype, 'createQuery');
    runQueryStub = sandbox.stub(DatastoreAPI.prototype, 'runQuery');
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('gets successfully', function() {
    const entities = ['strawberry', 'blueberry', 'blackberry', 'raspberry'];
    createQueryStub.returns('I would like some berries!');
    runQueryStub.returns(entities);
    assert.equal(datastore.getEntities(kind), entities);
    assert(runQueryStub.calledOnce);
    assert(runQueryStub.calledWith('I would like some berries!'));
  });
  it('throws error if createQuery throws error', function() {
    const createError = new Error('Could not create query.');
    createQueryStub.throws(createError);
    assert.throws(function() {
      datastore.getEntities(kind);
    }, createError);
  });
  it('throws error if runQuery throws error', function() {
    const runError = new Error('Could not run query.');
    createQueryStub.throws(runError);
    assert.throws(function() {
      datastore.getEntities(kind);
    }, runError);
  });
});

describe('datastore.getEntitiesWithFilter()', function() {
  const kind = 'Berries';
  const field = 'color';
  const value = 'red';
  const entities = ['strawberry', 'raspberry'];
  let createQueryStub;
  let runQueryStub;
  let filterStub;

  beforeEach(function() {
    createQueryStub = sandbox.stub(DatastoreAPI.prototype, 'createQuery');
    runQueryStub = sandbox.stub(DatastoreAPI.prototype, 'runQuery');
    filterStub = sandbox.stub().returns('red berries');
    createQueryStub.returns({filter: filterStub});
    runQueryStub.returns(entities);
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('gets successfully', function() {
    assert.equal(datastore.getEntitiesWithFilter(kind, field, value), entities);
    assert(createQueryStub.calledWith(kind));
    assert(filterStub.calledWith(field, value));
    assert(runQueryStub.calledWith('red berries'));
  });
  it('throws error if createQuery throws error', function() {
    const createError = new Error('Could not create query.');
    createQueryStub.throws(createError);
    assert.throws(function() {
      datastore.getEntitiesWithFilter(kind);
    }, createError);
  });
  it('throws error if runQuery throws error', function() {
    const runError = new Error('Could not run query.');
    createQueryStub.throws(runError);
    assert.throws(function() {
      datastore.getEntities(kind);
    }, runError);
  });
});

describe('datastore.getChildrenOfEntity()', function() {
  const kind = 'Berries';
  const parentPath = ['Fruit', 11];
  const entities = ['strawberry', 'blueberry', 'blackberry', 'raspberry'];
  const parentKey = {id: 11, path: parentPath};
  let keyStub;
  let createQueryStub;
  let hasAncestorStub;
  let runQueryStub;

  beforeEach(function() {
    keyStub = sandbox.stub(DatastoreAPI.prototype, 'key');
    keyStub.returns(parentKey);
    createQueryStub = sandbox.stub(DatastoreAPI.prototype, 'createQuery');
    runQueryStub = sandbox.stub(DatastoreAPI.prototype, 'runQuery');
    hasAncestorStub = sandbox.stub().returns('ancestor is fruit');
    createQueryStub.returns({hasAncestor: hasAncestorStub});
    runQueryStub.returns(entities);
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('gets successfully', function() {
    assert.equal(datastore.getChildrenOfEntity(parentPath, kind), entities);
    assert(keyStub.calledWith(parentPath));
    assert(createQueryStub.calledWith(kind));
    assert(hasAncestorStub.calledWith(parentKey));
    assert(runQueryStub.calledWith('ancestor is fruit'));
  });
  it('throws error if key throws error', function() {
    const keyError = new Error('Could not retrieve key.');
    keyStub.throws(keyError);
    assert.throws(function() {
      datastore.getChildrenOfEntity(parentPath, kind);
    }, keyError);
  });
  it('throws error if createQuery throws error', function() {
    const createError = new Error('Could not create query.');
    createQueryStub.throws(createError);
    assert.throws(function() {
      datastore.getChildrenOfEntity(parentPath, kind);
    }, createError);
  });
  it('throws error if hasAncestor throws error', function() {
    const ancestorError = new Error('Could not filter by ancestor.');
    hasAncestorStub.throws(ancestorError);
    assert.throws(function() {
      datastore.getChildrenOfEntity(parentPath, kind);
    }, ancestorError);
  });
  it('throws error if runQuery throws error', function() {
    const runError = new Error('Could not run query.');
    runQueryStub.throws(runError);
    assert.throws(function() {
      datastore.getChildrenOfEntity(parentPath, kind);
    }, runError);
  });
});

describe('datastore.createEntityKey()', function() {
  const path = ['Fruit', 11];
  const key = {id: 11, path: path};
  let keyStub;
  beforeEach(function() {
    keyStub = sandbox.stub(DatastoreAPI.prototype, 'key');
    keyStub.returns(key);
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('creates successfully', function() {
    assert.equal(datastore.createEntityKey(path), key);
  });
  it('throws error if create throws error', function() {
    const keyError = new Error('Could not create key.');
    keyStub.throws(keyError);
    assert.throws(function() {
      datastore.createEntityKey(path);
    }, keyError);
  });
});

describe('datastore.getEntityKey()', function() {
  const key = {id: 11, path: ['Fruit', 11]};
  const entity = {'kind': 'Fruit', '_key': key};
  let getKeyStub;
  beforeEach(function() {
    getKeyStub = sandbox.stub(DatastoreAPI.prototype, 'KEY').get(function() {
      return '_key';
    });
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('gets successfully', function() {
    assert.equal(datastore.getEntityKey(entity), key);
  });
});

describe('datastore.updateEntityField()', function() {
  const entityPath = ['Fruit', 11, 'Berries', 20];
  const entityKey = {id: 11, path: entityPath};
  const apiResponse = {success: true};
  let entity;
  let keyStub;
  let getStub;
  let updateStub;
  beforeEach(function() {
    entity = {name: 'raspberry', state: 'Oregon'};
    keyStub = sandbox.stub(DatastoreAPI.prototype, 'key');
    keyStub.returns(entityKey);
    getStub = sandbox.stub(DatastoreAPI.prototype, 'get');
    updateStub = sandbox.stub(DatastoreAPI.prototype, 'update');
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('updates existing field successfully', function() {
    getStub.resolves([entity]);
    updateStub.resolves(apiResponse);
    return datastore.updateEntityField(entityPath, 'state', 'Washington')
        .then(function(response) {
          expect(response).to.equal(apiResponse);
          assert(updateStub.calledWith({
            key: entityKey,
            data: {name: 'raspberry', state: 'Washington'}
          }));
        });
  });
  it('add new field successfully', function() {
    getStub.resolves([entity]);
    updateStub.resolves(apiResponse);
    return datastore.updateEntityField(entityPath, 'color', 'red')
        .then(function(response) {
          expect(response).to.equal(apiResponse);
          assert(updateStub.calledWith({
            key: entityKey,
            data: {name: 'raspberry', state: 'Oregon', color: 'red'}
          }));
        });
  });
  it('rejects Promise if get fails', function() {
    const error = new Error('Uh oh!');
    getStub.rejects(error);
    return datastore.updateEntityField(entityPath, 'state', 'Washington')
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.equal(error);
        });
  });
  it('rejects Promise if update fails', function() {
    const error = new Error('Uh oh!');
    getStub.resolves([entity]);
    updateStub.rejects(error);
    return datastore.updateEntityField(entityPath, 'state', 'Washington')
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.equal(error);
        });
  });
  it('rejects Promise if no entity found', function() {
    getStub.resolves([]);
    return datastore.updateEntityField(entityPath, 'state', 'Washington')
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
});

describe('datastore.updateEntity()', function() {
  const key = {id: 10, name: 'mango'};
  const data = {name: 'deployment', triggers: [{}, {}, {}]};
  let updateStub;

  beforeEach(function() {
    updateStub = sandbox.stub(DatastoreAPI.prototype, 'update');
  });
  afterEach(function() {
    sandbox.restore();
  });

  it('updates successfully', function() {
    updateStub.returns('Updated!');
    assert.equal(datastore.updateEntity(key, data), 'Updated!');
    const entity = {key: key, data: data};
    assert(updateStub.calledOnce);
    assert(updateStub.calledWith(entity));
  });
  it('throws error if update throws error', function() {
    const error = new Error('Uh oh!');
    updateStub.throws(error);
    assert.throws(function() {
      datastore.updateEntity(key, data);
    }, error);
  });
});

describe('datastore.deleteEntity()', function() {
  const key = {id: 10, name: 'mango'};
  let deleteStub;

  beforeEach(function() {
    deleteStub = sandbox.stub(DatastoreAPI.prototype, 'delete');
  });
  afterEach(function() {
    sandbox.restore();
  });

  it('deletes successfully', function() {
    deleteStub.returns('Deleted!');
    assert.equal(datastore.deleteEntity(key), 'Deleted!');
    assert(deleteStub.calledOnce);
    assert(deleteStub.calledWith(key));
  });
  it('throws error if delete throws error', function() {
    const error = new Error('Uh oh!');
    deleteStub.throws(error);
    assert.throws(function() {
      datastore.deleteEntity(key);
    }, error);
  });
});

describe('datastore.deleteChildrenOfEntity()', function() {
  const parentPath = ['Fruit', 11];
  const kind = 'Berries';
  let getChildrenOfEntityStub;
  let getEntityKeyStub;
  let deleteEntityStub;
  beforeEach(function() {
    getChildrenOfEntityStub = sandbox.stub(datastore, 'getChildrenOfEntity');
    getEntityKeyStub = sandbox.stub(datastore, 'getEntityKey');
    getEntityKeyStub.callsFake(function(entity) {
      return entity.key
    });
    deleteEntityStub = sandbox.stub(datastore, 'deleteEntity');
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('deletes nothing if entity has no children', function() {
    getChildrenOfEntityStub.resolves([[]]);
    return datastore.deleteChildrenOfEntity(parentPath, kind).then(function() {
      assert(deleteEntityStub.calledWith([]));
      assert(getEntityKeyStub.notCalled);
    });
  });
  it('deletes one child', function() {
    const children = [{key: {name: 'strawberry', id: 20}}];
    const childrenKeys = [{name: 'strawberry', id: 20}];
    const apiResponse = {success: true};
    getChildrenOfEntityStub.resolves([children]);
    deleteEntityStub.resolves(apiResponse);
    return datastore.deleteChildrenOfEntity(parentPath, kind)
        .then(function(response) {
          expect(response).to.equal(apiResponse);
          assert(getEntityKeyStub.calledOnce);
          assert(deleteEntityStub.calledWith(childrenKeys));
        });
  });
  it('deletes three children', function() {
    const children = [
      {key: {name: 'strawberry', id: 20}}, {key: {name: 'blackberry', id: 21}},
      {key: {name: 'raspberry', id: 22}}
    ];
    const childrenKeys = [
      {name: 'strawberry', id: 20}, {name: 'blackberry', id: 21},
      {name: 'raspberry', id: 22}
    ];
    const apiResponse = {success: true};
    getChildrenOfEntityStub.resolves([children]);
    deleteEntityStub.resolves(apiResponse);
    return datastore.deleteChildrenOfEntity(parentPath, kind)
        .then(function(response) {
          expect(response).to.equal(apiResponse);
          assert(getEntityKeyStub.calledThrice);
          assert(deleteEntityStub.calledWith(childrenKeys));
        });
  });
  it('rejects Promise if getChildrenOfEntity fails', function() {
    const error = new Error('Uh oh!');
    getChildrenOfEntityStub.rejects(error);
    return datastore.deleteChildrenOfEntity(parentPath, kind)
        .then(function(response) {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.equal(error);
        });
  });
  it('rejects Promise if deleteEntity fails', function() {
    const children = [{key: {name: 'strawberry', id: 20}}];
    getChildrenOfEntityStub.resolves([children]);
    const error = new Error('Uh oh!');
    deleteEntityStub.rejects(error);
    return datastore.deleteChildrenOfEntity(parentPath, kind)
        .then(function(response) {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.equal(error);
        });
  });
});

describe('datastore.findMissingFields()', function() {
  it('returns empty array if no fields are missing', function() {
    const object = {foo: 'a', bar: 'b', baz: 'c'};
    const requiredFields = ['foo', 'bar'];
    const missingFields = datastore.findMissingFields(requiredFields, object);
    assert.equal(missingFields.length, 0);
  });
  it('returns missing fields if fields are missing', function() {
    const object = {foo: 'a'};
    const requiredFields = ['foo', 'bar', 'baz'];
    const missingFields = datastore.findMissingFields(requiredFields, object);
    assert.sameMembers(missingFields, ['bar', 'baz']);
  });
  it('returns empty array if no fields are required', function() {
    const object = {foo: 'a', bar: 'b'};
    const requiredFields = [];
    const missingFields = datastore.findMissingFields(requiredFields, object);
    assert.equal(missingFields.length, 0);
  });
  it('returns missing fields if object is empty', function() {
    const object = {};
    const requiredFields = ['foo'];
    const missingFields = datastore.findMissingFields(requiredFields, object);
    assert.sameMembers(missingFields, ['foo']);
  });
});
