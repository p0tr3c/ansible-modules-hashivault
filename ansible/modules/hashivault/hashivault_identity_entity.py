#!/usr/bin/env python
DOCUMENTATION = '''
---
module: hashivault_identity_entity
version_added: "3.12.0"
short_description: Hashicorp Vault entity create module
description:
    - Module to manage identity entity in Hashicorp Vault.
options:
    url:
        description:
            - url for vault
        default: to environment variable VAULT_ADDR
    ca_cert:
        description:
            - "path to a PEM-encoded CA cert file to use to verify the Vault server TLS certificate"
        default: to environment variable VAULT_CACERT
    ca_path:
        description:
            - "path to a directory of PEM-encoded CA cert files to verify the Vault server TLS certificate : if ca_cert is specified, its value will take precedence"
        default: to environment variable VAULT_CAPATH
    client_cert:
        description:
            - "path to a PEM-encoded client certificate for TLS authentication to the Vault server"
        default: to environment variable VAULT_CLIENT_CERT
    client_key:
        description:
            - "path to an unencrypted PEM-encoded private key matching the client certificate"
        default: to environment variable VAULT_CLIENT_KEY
    verify:
        description:
            - "if set, do not verify presented TLS certificate before communicating with Vault server : setting this variable is not recommended except during testing"
        default: to environment variable VAULT_SKIP_VERIFY
    authtype:
        description:
            - "authentication type to use: token, userpass, github, ldap, approle"
        default: token
    token:
        description:
            - token for vault
        default: to environment variable VAULT_TOKEN
    username:
        description:
            - username to login to vault.
        default: to environment variable VAULT_USER
    password:
        description:
            - password to login to vault.
        default: to environment variable VAULT_PASSWORD
    name:
        description:
            - entity name to create or update.
    id:
        description:
            - entity id to update.
    metadata:
        description:
            - metadata to be associated with entity
    disabled:
        description:
            - whether the entity is disabled
        default: false
    policies:
        description:
            - entity policies.
        default: default
    state:
        description:
            - whether crete/update or delete the entity
'''
EXAMPLES = '''
---
- hosts: localhost
  tasks:
    - hashivault_identity_entity:
      name: 'bob'
      policies: 'bob'
'''


def main():
    argspec = hashivault_argspec()
    argspec['name'] = dict(required=False, type='str', default=None)
    argspec['id'] = dict(required=False, type='str', default=None)
    argspec['metadata'] = dict(required=False, type='dict', default={})
    argspec['disabled'] = dict(required=False, type='bool', default=False)
    argspec['policies'] = dict(required=False, type='list', default=[])
    argspec['state'] = dict(required=False, type='str', default='present')
    module = hashivault_init(argspec)
    result = hashivault_identity_entity(module.params)
    if result.get('failed'):
        module.fail_json(**result)
    else:
        module.exit_json(**result)


from ansible.module_utils.basic import *
from ansible.module_utils.hashivault import *

def hashivault_identity_entity_update(
    entity_details,
    client,
    entity_id,
    entity_name,
    entity_metadata,
    entity_disabled,
    entity_policies ):
    if  entity_details['data']['name'] != entity_name or \
        entity_details['data']['disabled'] != entity_disabled or \
        cmp(entity_details['data']['metadata'], entity_metadata) or \
        set(entity_details['data']['policies']) !=  set(entity_policies):
        client.secrets.identity.update_entity(
            entity_id=entity_id,
            name=entity_name,
            metadata=entity_metadata,
            policies=entity_policies,
            disabled=entity_disabled
        )
        return {'changed': True}
    else:
        return {'changed': False}

def hashivault_identity_entity_create(params):
    client = hashivault_auth_client(params)
    entity_name = params.get('name')
    entity_id = params.get('id')
    entity_metadata = params.get('metadata')
    entity_disabled = params.get('disabled')
    entity_policies = params.get('policies')

    if entity_id is not None:
        try:
            entity_details = client.secrets.identity.read_entity(
                entity_id=entity_id
            )
        except Exception as e:
            return {'failed': True, 'msg': e.message}
        else:
            return hashivault_identity_entity_update(entity_details, client,
                entity_name, entity_id, entity_metadata, entity_disabled,
                entity_policies)
    elif entity_name is not None:
        try:
            entity_details = client.secrets.identity.read_entity_by_name(
                name=entity_name
            )
        except:
            response = client.secrets.identity.create_or_update_entity_by_name(
                name=entity_name,
                metadata=entity_metadata,
                policies=entity_policies,
                disabled=entity_disabled
            )
        else:
            return hashivault_identity_entity_update(entity_details, client,
                entity_name=entity_name,
                entity_id=entity_details['data']['id'],
                entity_metadata=entity_metadata,
                entity_disabled=entity_disabled,
                entity_policies=entity_policies)
    else:
        return {'failed': True, 'msg': "Either name or id must be provided"}

    if hasattr(response, 'status_code'):
        if response.status_code == 204:
            return {'changed': False}
        else:
            return {'failed': True, 'msg': "Unkown response code"}
    else:
        entity_id = response['data']['id']
        return {'changed': True, 'data': response['data'] }

def hashivault_identity_entity_delete(params):
    client = hashivault_auth_client(params)
    entity_id = params.get('id')
    entity_name = params.get('name')

    if entity_id is not None:
        try:
            entity_details = client.secrets.identity.read_entity(
                entity_id=entity_id
            )
        except:
            return {'changed': False}
        else:
            client.secrets.identity.delete_entity(
               entity_id=entity_id
            )
            return {'changed': True}
    elif entity_name is not None:
        try:
            entity_details = client.secrets.identity.read_entity_by_name(
                name=entity_name
            )
        except:
            return {'changed': False}
        else:
            client.secrets.identity.delete_entity_by_name(
               name=entity_name
            )
            return {'changed': True}
    else:
        return {'failed': True, 'msg': "Either name or id must be provided"}

@hashiwrapper
def hashivault_identity_entity(params):
    state = params.get('state')
    if state == 'present':
        return hashivault_identity_entity_create(params)
    elif state == 'absent':
        return hashivault_identity_entity_delete(params)
    else:
        return {'failed': True, 'msg': 'Unknown state'}

if __name__ == '__main__':
    main()
