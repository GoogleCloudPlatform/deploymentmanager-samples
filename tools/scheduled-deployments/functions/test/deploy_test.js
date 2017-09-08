'use strict';

const assert = require('chai').assert;
const expect = require('chai').expect;
const sinon = require('sinon');
const datastore = require('../datastore');
const deploy = require('../deploy');
const google = require('googleapis');

const sandbox = sinon.createSandbox();


describe('deploy.deployConfig()', function() {
  // TODO: issue stubbing function in a 'then' statement
});

describe('deploy.deleteDeployment()', function() {
  // TODO: issue stubbing function in a 'then' statement
});

describe('deploy.getTriggers()', function() {
  const path = ['ScheduledDeployments', 123456];
  const scheduledDeployment = {name: 'test-deployment', path: path};
  let getEntityKeyStub;
  let getChildrenOfEntityStub;

  beforeEach(function() {
    getEntityKeyStub = sandbox.stub(datastore, 'getEntityKey');
    getChildrenOfEntityStub = sandbox.stub(datastore, 'getChildrenOfEntity');
    getEntityKeyStub.returns({path: path});
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('gets successfully', function() {
    const triggers =
        [{name: 'trigger-one'}, {name: 'trigger-two'}, {name: 'trigger-three'}];
    getChildrenOfEntityStub.resolves([triggers]);
    return deploy.getTriggers(scheduledDeployment)
        .then(function(returnedTriggers) {
          expect(returnedTriggers).to.equal(triggers);
        });
  });
  it('returns a rejected promise upon error', function() {
    const error = new Error('Uh oh!');
    getChildrenOfEntityStub.rejects(error);
    return deploy.getTriggers(scheduledDeployment).catch(function(err) {
      expect(err).to.equal(error);
    });
  });
});

describe('deploy.getActiveTriggers()', function() {
  let isTriggerFormatValidStub;
  let crontabWithinIntervalStub;
  let clock;
  let parent;

  beforeEach(function() {
    clock = sinon.useFakeTimers(Date.parse('2017-08-10 00:30:00'));
    parent = {id: 11, name: 'test-deployment'};
  });
  afterEach(function() {
    sandbox.restore();
    clock.restore();
  });
  it('returns an empty array if list of Triggers is empty', function() {
    const triggers = [];
    return deploy.getActiveTriggers(triggers, parent)
        .then(function(activeTriggers) {
          assert.equal(activeTriggers.length, 0);
        });
  });
  it('rejects Promise if any Trigger has an invalid format', function() {
    const triggers = [
      {
        'name': 'test-trigger',
        'type': 'timer',
        'time': '30 10 * * *',
        'action': 'CREATE_OR_UPDATE'
      },
      {
        'name': 'invalid-trigger',
        'type': 'timer',
        'time': '30 12 * * *',
        'action': 'THIS_IS_NOT_AN_ACTION'
      }
    ];
    return deploy.getActiveTriggers(triggers, parent)
        .then(function() {
          return Promise.reject('Promise was not supposed to succeed.');
        })
        .catch(function(err) {
          expect(err).to.exist;
        });
  });
  it('returns an empty array if no Triggers are active', function() {
    parent.lastDeployed = Date.parse('2017-08-10 00:25:00');
    const triggers = [
      {
        'name': 'first-trigger',
        'type': 'timer',
        'time': '20 0 * * *',
        'action': 'CREATE_OR_UPDATE'
      },
      {
        'name': 'second-trigger',
        'type': 'timer',
        'time': '30 0 9 8 *',
        'action': 'CREATE_OR_UPDATE'
      }
    ];
    return deploy.getActiveTriggers(triggers, parent)
        .then(function(activeTriggers) {
          assert.equal(activeTriggers.length, 0);
        });
  });
  it('returns a single active Trigger', function() {
    parent.lastDeployed = Date.parse('2017-08-10 00:20:00');
    const trigger1 = {
      'name': 'create-trigger',
      'type': 'timer',
      'time': '20 0 * * *',
      'action': 'CREATE_OR_UPDATE'
    };
    const trigger2 = {
      'name': 'delete-trigger',
      'type': 'timer',
      'time': '30 0 * * *',
      'action': 'DELETE'
    };
    return deploy.getActiveTriggers([trigger1, trigger2], parent)
        .then(function(activeTriggers) {
          assert.equal(activeTriggers.length, 1);
          assert.deepEqual(
              activeTriggers[0],
              {timestamp: Date.parse('2017-08-10 00:30:00'), entity: trigger2});
        });
  });
  it('returns two active triggers', function() {
    parent.lastDeployed = Date.parse('2017-08-10 00:20:00');
    const trigger1 = {
      'name': 'create-trigger',
      'type': 'timer',
      'time': '33 0 * * *',
      'action': 'CREATE_OR_UPDATE'
    };
    const trigger2 = {
      'name': 'delete-trigger',
      'type': 'timer',
      'time': '34 0 * * *',
      'action': 'DELETE'
    };
    return deploy.getActiveTriggers([trigger1, trigger2], parent)
        .then(function(activeTriggers) {
          assert.equal(activeTriggers.length, 2);
          assert.deepEqual(activeTriggers, [
            {timestamp: Date.parse('2017-08-10 00:33:00'), entity: trigger1},
            {timestamp: Date.parse('2017-08-10 00:34:00'), entity: trigger2}
          ]);
        });
  });
});

describe('deploy.processActiveTriggers()', function() {
  const parent = {id: 11, name: 'test-deployment'};
  const timestamp = (new Date()).getTime();
  const laterTimestamp = timestamp + 1;
  let getEntityKeyStub;
  let deployConfigStub;
  let deleteDeploymentStub;

  beforeEach(function() {
    deployConfigStub = sandbox.stub(deploy, 'deployConfig');
    deleteDeploymentStub = sandbox.stub(deploy, 'deleteDeployment');
    getEntityKeyStub = sandbox.stub(datastore, 'getEntityKey');
    getEntityKeyStub.returns({id: 11});
  });
  afterEach(function() {
    sandbox.restore();
  });
  it('takes no action if list of triggers is empty', function() {
    const triggers = [];
    deploy.processActiveTriggers(triggers, parent);
    assert.equal(deployConfigStub.callCount, 0);
    assert.equal(deleteDeploymentStub.callCount, 0);
  });
  it('invokes deployment if latest active trigger is CREATE_OR_UPDATE',
     function() {
       const createTrigger = {
         timestamp: laterTimestamp,
         entity: {
           'name': 'create-trigger',
           'type': 'timer',
           'time': '34 0 * * *',
           'action': 'CREATE_OR_UPDATE'
         }
       };
       const deleteTrigger = {
         timestamp: timestamp,
         entity: {
           'name': 'delete-trigger',
           'type': 'timer',
           'time': '33 0 * * *',
           'action': 'DELETE'
         }
       };
       deploy.processActiveTriggers([createTrigger, deleteTrigger], parent);
       assert.equal(deleteDeploymentStub.callCount, 0);
       assert.equal(deployConfigStub.callCount, 1);
       assert(deployConfigStub.calledWith(createTrigger.entity));
     });
  it('invokes deployment deletion if latest active trigger is DELETE',
     function() {
       const triggers = [
         {
           timestamp: timestamp,
           entity: {
             'name': 'create-trigger',
             'type': 'timer',
             'time': '33 0 * * *',
             'action': 'CREATE_OR_UPDATE'
           }
         },
         {
           timestamp: laterTimestamp,
           entity: {
             'name': 'delete-trigger',
             'type': 'timer',
             'time': '34 0 * * *',
             'action': 'DELETE'
           }
         }
       ];
       deploy.processActiveTriggers(triggers, parent);
       assert.equal(deployConfigStub.callCount, 0);
       assert.equal(deleteDeploymentStub.callCount, 1);
     });
});

describe('deploy.crontabWithinInterval()', function() {
  const range = 10;  // minutes between Cron events
  const lastDeployed = Date.parse('2017-08-10 00:00:00');

  it('make deployment now', function() {
    const time = Date.parse('2017-08-10 00:15:00');
    const crontab = '* * * * *';
    return deploy.crontabWithinInterval(time, range, crontab, lastDeployed)
        .then(function(response) {
          expect(response).to.equal(time);
        })
  });
  it('make upcoming deployment at edge of time interval', function() {
    const time = Date.parse('2017-08-10 00:15:00');
    const crontab = '10 * * * *';
    return deploy.crontabWithinInterval(time, range, crontab, lastDeployed)
        .then(function(response) {
          expect(response).to.equal(Date.parse('2017-08-10 00:10:00'));
        });
  });
  it('make previous deployment at edge of time interval', function() {
    const time = Date.parse('2017-08-10 00:35:00');
    const crontab = '30 * * * *';
    return deploy.crontabWithinInterval(time, range, crontab, lastDeployed)
        .then(function(response) {
          expect(response).to.equal(Date.parse('2017-08-10 00:30:00'));
        });
  });
  it('make a missed deployment; time is past interval end', function() {
    const time = Date.parse('2017-08-10 10:35:01');
    const crontab = '30 10 * * *';
    return deploy.crontabWithinInterval(time, range, crontab, lastDeployed)
        .then(function(response) {
          expect(response).to.equal(Date.parse('2017-08-10 10:30:00'));
        });
  });
  it('no deployment; time is past interval start', function() {
    const time = Date.parse('2017-08-10 00:24:59');
    const crontab = '30 * * * *';
    return deploy.crontabWithinInterval(time, range, crontab, lastDeployed)
        .then(function(response) {
          expect(response).to.equal(0);
        });
  });
  it('interprets fancy crontab', function() {
    const time = Date.parse('2017-08-10 03:16:00');
    const crontab = '20 3,9 10-15 Aug *';
    return deploy.crontabWithinInterval(time, range, crontab, lastDeployed)
        .then(function(response) {
          expect(response).to.equal(Date.parse('2017-08-10 03:20:00'));
        });
  });
});

describe('deploy.compareTriggers()', function() {
  const one = {
    timestamp: Date.parse('2017-08-10 00:01:00'),
    entity: {name: 'apple'}
  };
  const two = {
    timestamp: Date.parse('2017-08-10 00:02:00'),
    entity: {name: 'banana'}
  };
  const three = {
    timestamp: Date.parse('2017-08-10 00:01:00'),
    entity: {name: 'banana'}
  };

  it('prioritizes later timestamp as first parameter', function() {
    const response = deploy.compareTriggers(two, one);
    assert.equal(response, -1);
  });
  it('prioritizes later timestamp as second parameter', function() {
    const response = deploy.compareTriggers(one, two);
    assert.equal(response, 1);
  });
  it('prioritizes first parameter with later alphabetical name if timestamps equal',
     function() {
       const response = deploy.compareTriggers(three, one);
       assert.equal(response, -1);
     });
  it('prioritizes second parameter with later alphabetical name if timestamps equal',
     function() {
       const response = deploy.compareTriggers(one, three);
       assert.equal(response, 1);
     });
  it('gives equal priority to identical timestamps and names', function() {
    const response = deploy.compareTriggers(one, one);
    assert.equal(response, 0);
  });
});
