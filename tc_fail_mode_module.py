#!/usr/bin/python

ANSIBLE_METADATA = {
    'metadata_version': '1.1',
    'status': ['preview'],
    'supported_by': 'community'
}

DOCUMENTATION = '''
---
module: my_sample_module

short_description: This is my sample module

version_added: "2.4"

description:
    - "This is my longer description explaining my sample module"

options:
    name:
        description:
            - This is the message to send to the sample module
        required: true
    new:
        description:
            - Control to demo if the result of this module is changed or not
        required: false

extends_documentation_fragment:
    - azure

author:
    - Your Name (@yourhandle)
'''

EXAMPLES = '''
# Pass in a message
- name: Test with a message
  my_new_test_module:
    name: hello world

# pass in a message and have changed true
- name: Test with a message and changed output
  my_new_test_module:
    name: hello world
    new: true

# fail the module
- name: Test failure of the module
  my_new_test_module:
    name: fail me
'''

RETURN = '''
original_message:
    description: The original name param that was passed in
    type: str
message:
    description: The output message that the sample module generates
'''

import datetime
import glob
import os
import shlex

from ansible.module_utils.basic import AnsibleModule


def run_module():
    # the command module is the one ansible module that does not take key=value args
    # hence don't copy this one if you are looking to build others!
    module = AnsibleModule(
        argument_spec=dict(
            _uses_shell=dict(type='bool', default=False),
            interface=dict(type='str', required=True),
            withheld_period=dict(type='str', default="5"),
            ## TODO (Add fail mode type param)
            executable=dict(),
            # The default for this really comes from the action plugin
            stdin=dict(required=False),
        )
    )

    shell = module.params['_uses_shell']
    executable = module.params['executable']
    stdin = module.params['stdin']
    interface = module.params['interface']
    withheld_period = module.params['withheld_period']

    set_args = shlex.split("tcset --device %s --delay 10ms" % interface)
    sleep_args = shlex.split("sleep %s" % withheld_period)
    unset_args = shlex.split("tcdel --device %s" % interface)

    startd = datetime.datetime.now()
    rc, out, err = module.run_command(set_args, executable=executable,
                                      use_unsafe_shell=shell,
                                      encoding=None, data=stdin)

    if rc != 0:
        endd = datetime.datetime.now()
        delta = endd - startd
        result = dict(
            cmd=set_args,
            stdout=out.rstrip(b"\r\n"),
            stderr=err.rstrip(b"\r\n"),
            rc=rc,
            start=str(startd),
            end=str(endd),
            delta=str(delta),
            changed=True,
        )
        module.fail_json(msg='non-zero return code', **result)

    rc, out, err = module.run_command(sleep_args, executable=executable,
                                      use_unsafe_shell=shell,
                                      encoding=None, data=stdin)

    rc, out, err = module.run_command(unset_args, executable=executable,
                                      use_unsafe_shell=shell,
                                      encoding=None, data=stdin)
    if rc != 0:
        endd = datetime.datetime.now()
        delta = endd - startd
        result = dict(
            cmd=set_args,
            stdout=out.rstrip(b"\r\n"),
            stderr=err.rstrip(b"\r\n"),
            rc=rc,
            start=str(startd),
            end=str(endd),
            delta=str(delta),
            changed=True,
        )
        module.fail_json(msg='non-zero return code', **result)

    endd = datetime.datetime.now()
    delta = endd - startd

    result = dict(
        cmd=set_args,
        stdout=out.rstrip(b"\r\n"),
        stderr=err.rstrip(b"\r\n"),
        rc=rc,
        start=str(startd),
        end=str(endd),
        delta=str(delta),
        changed=True,
    )

    if rc != 0:
        module.fail_json(msg='non-zero return code', **result)

    module.exit_json(**result)


def main():
    run_module()


if __name__ == '__main__':
    main()
