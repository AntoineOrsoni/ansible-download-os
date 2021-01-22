from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_lines,
)
from ansible_collections.cisco.ios.plugins.module_utils.network.ios.ios import (
    run_commands,
)

SKIP_LINES = ['Directory of', 'bytes total']
EMPTY_DIR = 'No files in directory'

def list_files(module, path, result, get_md5=False):
    command = {'command': f'dir {path}'}
    responses = run_commands(module, command)
    files = []
    for idx,response in enumerate(to_lines(responses)):
        for line in response:
            if not line or any(word in line for word in SKIP_LINES):
                continue
            if EMPTY_DIR in line:
                result['warnings'].append(f"Directory {path} is currently empty")
                break
            item_info = line.split()
            if len(item_info) != 9:
                result['warnings'].append(f"Could not parse content of {path}, please report this. Output was: {responses[idx]}. Offending line seems to be: {line}")
                break
            if 'd' in item_info[1]:
                # This is a directory
                continue
            filename = item_info[-1]
            files.append(filename)
    if get_md5:
        file_hashes = {}
        for f in files:
            remote_md5 = get_file_md5(module, f"{path}/{f}", result)
            if not remote_md5:
                # Skip this file if MD5 could not be retrieved.
                continue
            file_hashes[f] = remote_md5
        result.update({'files': file_hashes})
    else:
        result.update({'files': files})

def get_file_md5(module, path, result):
    command = {'command': f'verify /md5 {path}'}
    responses = run_commands(module, command)
    for idx,response in enumerate(to_lines(responses)):
        for line in response:
            if line.startswith('verify /md5'):
                remote_md5 = line.split()[-1]
                return remote_md5
        result['warnings'].append(f"Could not parse device output to get MD5 hash of {path}, please report this. File will be skipped. Output was: {responses[idx]}. Offending line seems to be: {line}")
    return None

def verify_md5(module, path, md5, result):
    remote_md5 = get_file_md5(module, path, result)
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
        verify_md5(module, path, md5, result)

    module.exit_json(**result)

if __name__ == "__main__":
    main()