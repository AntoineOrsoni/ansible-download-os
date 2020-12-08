from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_lines,
)
from ansible_collections.cisco.ios.plugins.module_utils.network.ios.ios import (
    run_commands,
)

def create_directory(module, path, result):
    command = {'command': f'mkdir {path}', 'prompt':'Create directory', 'answer':''}
    response = run_commands(module, command)[0]
    result.update({"changed": True})

def exists(module, path, result):
    command = {'command': f'dir {path}'}
    response = run_commands(module, command, check_rc=False)[0]
    if 'No such file or directory' in response:
        return False
    elif 'Error' in response:
        msg = "Could check for directory presence on device"
        module.fail_json(msg=msg, stdout=response)
    return True

def main():
    argument_spec = dict(
        directory=dict(type="str", required=True)
        )
    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=False
    )
    result = { "changed": False,
               "warnings": list()}

    # Build directory list to create
    dirnames = module.params["directory"].split('/')
    directories = []
    for i in range(2,len(dirnames)+1):
        directories.append('/'.join(dirnames[:i]))

    for directory in directories:
        if not exists(module, directory, result):
            create_directory(module, directory, result)
    module.exit_json(**result)

if __name__ == "__main__":
    main()