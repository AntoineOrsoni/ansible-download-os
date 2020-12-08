from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_lines,
)
from ansible_collections.cisco.ios.plugins.module_utils.network.ios.ios import (
    run_commands,
)

def list_files(module, path, result, get_md5=False):
    command = {'command': f'dir {path}'}
    responses = run_commands(module, command)
    lines = list(to_lines(responses))[0]
    files = []
    for line in lines[2:-2]:
        if 'No files in directory' in line:
            break
        if 'd' not in line.split()[1]:
            # This is a file, not a directory
            files.append(line.split()[-1])
    if get_md5:
        file_hashes = {}
        for f in files:
            remote_md5 = get_file_md5(module, f"{path}/{f}")
            file_hashes[f] = remote_md5
        result.update({'files': file_hashes})
    else:
        result.update({'files': files})

def get_file_md5(module, path):
    command = {'command': f'verify /md5 {path}'}
    responses = run_commands(module, command)
    remote_md5 = list(to_lines(responses))[0][1].split()[-1]
    return remote_md5

def verify_md5(module, path, md5):
    remote_md5 = get_file_md5(module, path)
    if md5 != remote_md5:
        module.fail_json(msg=f'File {path} has wrong MD5 hash. Got {remote_md5}, expected {md5}')

def main():
    argument_spec = dict(
        list_files=dict(
            type='dict',
            options=dict(directory=dict(type='str', required=True),
                        get_md5=dict(type='bool', default=False)
            )
        ),
        verify=dict(
            type='dict',
            options=dict(file=dict(type='str', required=True),
                    expected_md5=dict(type='str', required=True)
            )
        )
    )
    module = AnsibleModule(
        argument_spec=argument_spec, supports_check_mode=False
    )
    result = { "changed": False,
               "warnings": list() }
    
    # List files on device
    if module.params["list_files"]:
        path = module.params["list_files"]["directory"]
        get_md5 = module.params["list_files"]["get_md5"]
        list_files(module, path, result, get_md5=get_md5)

    # Verify provided MD5 hashes
    if module.params["verify"]:
        path = module.params["verify"]["file"]
        md5 = module.params["verify"]["expected_md5"]
        verify_md5(module, path, md5)

    module.exit_json(**result)

if __name__ == "__main__":
    main()