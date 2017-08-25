"""Unit tests for `project.py`"""

import unittest
from project import MergeCallingServiceAccountWithOwnerPermissinsIntoBindings

class ProjectTestCase(unittest.TestCase):
  """Tests for `project.py`."""
  def test_merge_no_iam_policies(self):
    """Test output of the function when there are no IAM policies in the
      properties"""
    env = {'project_number': '123'}
    properties = {}
    expected = {
        'bindings': [
            {
                'role': 'roles/owner',
                'members':
                    ['serviceAccount:123@cloudservices.gserviceaccount.com']
            }
        ]
    }
    self.assertEqual(expected,
                     MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                         env, properties))

  def test_merge_with_existing_non_owner_policy(self):
    """Test output of the function when there are existing non owner IAM
      policies in the properties"""
    env = {'project_number': '123'}
    properties = {
        'iam-policy': {
            'bindings': [
                {
                    'role': 'roles/viewer',
                    'members': ['user:foobar@barbaz.com']
                }
            ]
        }
    }
    expected = {
        'bindings': [
            {
                'role': 'roles/viewer',
                'members': ['user:foobar@barbaz.com']
            },
            {
                'role': 'roles/owner',
                'members':
                    ['serviceAccount:123@cloudservices.gserviceaccount.com']
            }
        ]
    }
    self.assertEqual(expected,
                     MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                         env, properties))

  def test_merge_with_different_owner_policy(self):
    """Test output of the function when there is an existing but different
      owner IAM policy in the properties"""
    env = {'project_number': '123'}
    properties = {
        'iam-policy': {
            'bindings': [
                {
                    'role': 'roles/owner',
                    'members': ['user:foobar@barbaz.com']
                }
            ]
        }
    }
    expected = {
        'bindings': [
            {
                'role': 'roles/owner',
                'members': ['user:foobar@barbaz.com',
                            ('serviceAccount:123@cloudservices'
                             '.gserviceaccount.com')]
            }
        ]
    }
    self.assertEqual(expected,
                     MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                         env, properties))

  def test_merge_with_same_owner_policy(self):
    """Test output of the function when the exact same policy already exists"""
    env = {'project_number': '123'}
    properties = {
        'iam-policy': {
            'bindings': [
                {
                    'role': 'roles/viewer',
                    'members': ['user:foobar@barbaz.com']
                },
                {
                    'role': 'roles/owner',
                    'members': ['user:foobar@barbaz.com',
                                ('serviceAccount:123@cloudservices'
                                 '.gserviceaccount.com')]
                }
            ]
        }
    }
    expected = {
        'bindings': [
            {
                'role': 'roles/viewer',
                'members': ['user:foobar@barbaz.com']
            },
            {
                'role': 'roles/owner',
                'members': ['user:foobar@barbaz.com',
                            ('serviceAccount:123@cloudservices'
                             '.gserviceaccount.com')]
            }
        ]
    }
    self.assertEqual(expected,
                     MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                         env, properties))

  def test_merge_with_missing_bindings_but_other_key_present(self):
    """"Test the function when there are no bindings in the iam policy block
        but some other unknown key exists"""
    env = {'project_number': '123'}
    properties = {
        'iam-policy': {
            'foobar': {
                'strangekey': 1
            }
        }
    }
    expected = {
        'foobar': {
            'strangekey': 1
        },
        'bindings': [
            {
                'role': 'roles/owner',
                'members': [('serviceAccount:123@cloudservices'
                             '.gserviceaccount.com')]
            }
        ]
    }
    self.assertEqual(expected,
                     MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                         env, properties))

  def test_merge_with_different_owner_policy_and_other_key(self):
    """Test output of the function when there is an existing but different
      owner IAM policy in the properties and some unknown key that exists"""
    env = {'project_number': '123'}
    properties = {
        'iam-policy': {
            'foobar': {
                'strangekey': 1
            },
            'bindings': [
                {
                    'role': 'roles/owner',
                    'members': ['user:foobar@barbaz.com']
                }
            ]
        }
    }
    expected = {
        'foobar': {
            'strangekey': 1
        },
        'bindings': [
            {
                'role': 'roles/owner',
                'members': ['user:foobar@barbaz.com',
                            ('serviceAccount:123@cloudservices'
                             '.gserviceaccount.com')]
            }
        ]
    }
    self.assertEqual(expected,
                     MergeCallingServiceAccountWithOwnerPermissinsIntoBindings(
                         env, properties))

if __name__ == '__main__':
  unittest.main()
