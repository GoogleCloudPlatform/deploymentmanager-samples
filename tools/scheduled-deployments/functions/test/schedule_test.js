const assert = require('chai').assert;
const expect = require('chai').expect;
const sinon = require('sinon');
const base64 = require('js-base64');
const datastore = require('../datastore');
const schedule = require('../schedule');

const sandbox = sinon.createSandbox();


describe('schedule.create()', function() {
  // TODO: issue stubbing function in a 'then' statement
});

describe('schedule.read()', function() {
  const name = 'test-deployment';
  const entity = {triggers: []};
  let jsonStub;
  let statusStub;
  let statusEndStub;
  let res;
  beforeEach(function() {
    jsonStub = sandbox.stub();
    statusEndStub = sandbox.stub();
    statusStub = sandbox.stub().returns({end: statusEndStub});
    res = {status: statusStub, json: jsonStub};
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('reads successfully', function() {
    schedule.read(name, entity, res);
    assert(statusStub.calledOnce);
    assert(statusStub.calledWith(200));
    assert(statusEndStub.calledOnce);
  });
});

describe('schedule.update()', function() {
  // TODO: issue stubbing function in a 'then' statement
});

describe('schedule.delete()', function() {
  // TODO: issue stubbing function in a 'then' statement
});


describe('schedule.enforceUniqueDeploymentName()', function() {
  const name = 'test-deployment';
  let getEntitiesWithFilterStub;
  beforeEach(function() {
    getEntitiesWithFilterStub =
        sandbox.stub(datastore, 'getEntitiesWithFilter');
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('resolves Promise if deployment name is unique', function() {
    getEntitiesWithFilterStub.resolves([[]]);
    return schedule.enforceUniqueDeploymentName(name)
        .then(function(result) {
          assert.isUndefined(result);
        })
        .catch(function(err) {
          return Promise.reject('Method was supposed to succeed.');
        });
  });
  it('rejects Promise if is not unique', function() {
    getEntitiesWithFilterStub.resolves([[{name: 'test-deployment', id: 11}]]);
    return schedule.enforceUniqueDeploymentName(name)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
  it('rejects Promise if getEntitiesWithFilter fails', function() {
    const error = new Error('Uh oh!');
    getEntitiesWithFilterStub.rejects(error);
    return schedule.enforceUniqueDeploymentName(name)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.equal(error);
        });
  });
});

function setupTriggerEntity(
    name, type, time, action, description, submitted, config, importName,
    importContent) {
  const entity = [
    {name: 'name', value: name}, {name: 'type', value: type},
    {name: 'time', value: time}, {name: 'action', value: action},
    {name: 'description', value: description},
    {name: 'submitted', value: submitted}
  ];
  if (config) {
    entity.push({name: 'config', value: config});
    if (importName) {
      entity.push({name: 'importName', value: importName});
      entity.push({name: 'importContent', value: importContent});
    }
  }
  return entity;
}

describe('schedule.putTriggerEntities()', function() {
  const parentName = 'test-deployment';
  const parentKey = {kind: 'ScheduledDeployment', id: 123456};
  const entityKey = {kind: 'Trigger', id: 1};
  const now = new Date();
  let isTriggerFormatValidStub;
  let createEntityKeyStub;
  let insertEntityStub;
  let clock;
  beforeEach(function() {
    isTriggerFormatValidStub = sandbox.stub(schedule, 'isTriggerFormatValid');
    createEntityKeyStub = sandbox.stub(datastore, 'createEntityKey');
    insertEntityStub = sandbox.stub(datastore, 'insertEntity');
    clock = sinon.useFakeTimers(now);
  });
  afterEach(function() {
    sandbox.restore();
    clock.restore();
  });
  it('handles zero triggers', function() {
    isTriggerFormatValidStub.resolves();
    const triggers = [];
    return schedule.putTriggerEntities(parentName, parentKey, triggers)
        .then(function() {
          assert(isTriggerFormatValidStub.notCalled);
          assert(insertEntityStub.notCalled);
        });
  });
  it('handles single DELETE trigger', function() {
    isTriggerFormatValidStub.resolves();
    createEntityKeyStub.returns(entityKey);
    const triggers = [{
      name: 'trigger-one',
      type: 'timer',
      time: '* * * * *',
      action: 'DELETE',
      description: 'first trigger'
    }];
    return schedule.putTriggerEntities(parentName, parentKey, triggers)
        .then(function() {
          assert(isTriggerFormatValidStub.called);
          assert(insertEntityStub.calledWith(
              entityKey,
              setupTriggerEntity(
                  'trigger-one', 'timer', '* * * * *', 'DELETE',
                  'first trigger', now.toISOString())));
        });
  });
  it('handles single CREATE_OR_UPDATE trigger', function() {
    isTriggerFormatValidStub.resolves();
    createEntityKeyStub.returns(entityKey);
    const triggers = [{
      name: 'trigger-three',
      type: 'timer',
      time: '* * * * *',
      action: 'CREATE_OR_UPDATE',
      description: 'third trigger',
      config: 'config details'
    }];
    return schedule.putTriggerEntities(parentName, parentKey, triggers)
        .then(function() {
          assert(isTriggerFormatValidStub.called);
          assert(insertEntityStub.calledWith(
              entityKey,
              setupTriggerEntity(
                  'trigger-three', 'timer', '* * * * *', 'CREATE_OR_UPDATE',
                  'third trigger', now.toISOString(), 'config details')));
        });
  });
  it('handles three triggers', function() {
    isTriggerFormatValidStub.resolves();
    createEntityKeyStub.returns(entityKey);
    const triggers = [
      {
        name: 'trigger-one',
        type: 'timer',
        time: '* * * * *',
        action: 'DELETE',
        description: 'first trigger'
      },
      {
        name: 'trigger-two',
        type: 'timer',
        time: '* * * * *',
        action: 'DELETE',
        description: 'second trigger'
      },
      {
        name: 'trigger-three',
        type: 'timer',
        time: '* * * * *',
        action: 'CREATE_OR_UPDATE',
        description: 'third trigger',
        config: 'config details'
      }
    ];
    return schedule.putTriggerEntities(parentName, parentKey, triggers)
        .then(function() {
          assert(isTriggerFormatValidStub.calledThrice);
          assert(insertEntityStub.calledThrice);
          assert(insertEntityStub.calledWith(
              entityKey,
              setupTriggerEntity(
                  'trigger-one', 'timer', '* * * * *', 'DELETE',
                  'first trigger', now.toISOString())));
          assert(insertEntityStub.calledWith(
              entityKey,
              setupTriggerEntity(
                  'trigger-two', 'timer', '* * * * *', 'DELETE',
                  'second trigger', now.toISOString())));
          assert(insertEntityStub.calledWith(
              entityKey,
              setupTriggerEntity(
                  'trigger-three', 'timer', '* * * * *', 'CREATE_OR_UPDATE',
                  'third trigger', now.toISOString(), 'config details')));
        });
  });
  it('rejects Promise if trigger format is invalid', function() {
    isTriggerFormatValidStub.rejects();
    createEntityKeyStub.returns(entityKey);
    const triggers = [{name: 'invalid trigger'}];
    return schedule.putTriggerEntities(parentName, parentKey, triggers)
        .then(function() {
          assert(insertEntityStub.notCalled);
        });
  });
});

describe('schedule.isTriggerFormatValid()', function() {
  it('contains required fields and action is CREATE_OR_UPDATE', function() {
    const trigger = {
      'name': 'my-trigger',
      'type': 'timer',
      'action': 'CREATE_OR_UPDATE',
      'time': '30 10 * * *'
    };
    return schedule.isTriggerFormatValid(trigger).then(function(result) {
      assert.equal(result, true);
    });
  });
  it('contains required fields and action is DELETE', function() {
    const trigger = {
      'name': 'your-trigger',
      'type': 'timer',
      'action': 'DELETE',
      'time': '30 10 * * *'
    };
    return schedule.isTriggerFormatValid(trigger).then(function(result) {
      assert.equal(result, true);
    });
  });
  it('contains required fields but action is invalid', function() {
    const trigger = {
      'name': 'Tigger',
      'type': 'timer',
      'action': 'BOUNCE',
      'time': '30 10 * * *'
    };
    return schedule.isTriggerFormatValid(trigger)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
  it('is missing a name field', function() {
    const trigger = {
      'type': 'timer',
      'action': 'CREATE_OR_UPDATE',
      'time': '30 10 * * *'
    };
    return schedule.isTriggerFormatValid(trigger)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
  it('is missing a type field', function() {
    const trigger = {
      'name': 'our-trigger',
      'action': 'CREATE_OR_UPDATE',
      'time': '30 10 * * *'
    };
    return schedule.isTriggerFormatValid(trigger)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
  it('is missing an action field', function() {
    const trigger = {
      'name': 'our-trigger',
      'type': 'timer',
      'time': '30 10 * * *'
    };
    return schedule.isTriggerFormatValid(trigger)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
  it('is missing a time field', function() {
    const trigger = {
      'name': 'our-trigger',
      'type': 'timer',
      'action': 'CREATE_OR_UPDATE'
    };
    return schedule.isTriggerFormatValid(trigger)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
});

describe('schedule.parseNameFromUrl()', function() {
  it('parses a query (POST)', function() {
    const url = '?=bob-dylan';
    assert.equal(schedule.parseNameFromUrl(url, 'POST'), 'bob-dylan');
  });
  it('parses a path', function() {
    const url = '/chuck-berry';
    assert.equal(schedule.parseNameFromUrl(url, 'GET'), 'chuck-berry');
  });
});
