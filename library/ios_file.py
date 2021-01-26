from ansible.module_utils.basic import AnsibleModule
from ansible_collections.ansible.netcommon.plugins.module_utils.network.common.utils import (
    to_lines,
)
from ansible_collections.cisco.ios.plugins.module_utils.network.ios.ios import (
    run_commands,
)

DOCUMENTATION = """
module: ios_file
author: Matthieu Tâche (mtache@cisco.com)
short_description: List existing files on Cisco IOS filesystem
description:
- This simple module provides a handy way to list existing files on Cisco IOS filesystem,
retrieve MD5 hashes and verify them against expected values.
version_added: 1.0.0
options:
  file:
    description:
    - The path of a file on the device. The module will verify if the file exists
      and return the result. Please note that the module will never fail
      if the file does not exist.
    type: path
  directory:
    description:
    - The path of a directory on the device. The module will list all files in the directory
      and return the list as a result. Please note that the module will never fail
      if the folder is empty or if the directory does not exist.
    type: path
  get_md5:
    description:
    - Specify whether MD5 hashes needs to be generated on the device when using the `file`
      or `directory` options.
    type: boolean
    default: False
  expected_md5:
    description:
    - The expected MD5 hash. Need to be used with the file option. The module will verify
      the file integrity on the device from an expected MD5 hash. The module will fail if
      the MD5 hashes do not match.
    type: str
"""
EXAMPLES = """
- name: Verify if a file exists and get its MD5 hash
  ios_file:
    file: bootflash:/ImageTarget/16.12.04/asr900rsp3-universalk9_npe.16.12.04.SPA.bin
    get_md5: True
- name: List all files in bootflash:/
  ios_file:
    direcotry: bootflash:/
- name: Verify a file integrity
  ios_file:
    file: bootflash:/ImageTarget/16.12.04/asr900rsp3-universalk9_npe.16.12.04.SPA.bin
    expected_md5: b38b6f41f9124281500834359ddb0d0a
"""
RETURN = """
files:
  description: The files present on the device.
  returned: when get_md5 is False and file or directory option is used
  type: list
  sample: TODO
files:
  description: The files present on the device as keys and their MD5 hashes as values.
  returned: when get_md5 is True and file or directory option is used
  type: dict
  sample: TODO
"""

SKIP_LINES = ['Directory of', 'bytes total']
EMPTY_DIR = 'No files in directory'
NOT_EXIST = 'No such file or directory'

def _parse_directory(module, result, dir_pathj):
    command = {'command': f'dir {dir_pathj}'}
    responses = run_commands(module, command)
    files = []
    for idx,response in enumerate(to_lines(responses)):
        for line in response:
            if NOT_EXIST in line:
                module.fail_json(msg=f'Directory {dir_pathj} does not exists on device.')
            if not line or any(word in line for word in SKIP_LINES):
                continue
            if EMPTY_DIR in line:
                result['warnings'].append(f"Directory {dir_pathj} is currently empty")
                break
            item_info = line.split()
            if len(item_info) != 9:
                result['warnings'].append(f"Could not parse content of {dir_pathj}, please report this. Output was: {responses[idx]}. Offending line seems to be: {line}")
                break
            if 'd' in item_info[1]:
                # This is a directory
                continue
            filename = item_info[-1]
            files.append(filename)
    return files

def _parse_file(module, result, file_path):
    command = {'command': f'dir {file_path}'}
    responses = run_commands(module, command)
    filename = None
    for idx,response in enumerate(to_lines(responses)):
        for line in response:
            if NOT_EXIST in line:
                break
            if not line or any(word in line for word in SKIP_LINES):
                continue
            item_info = line.split()
            if len(item_info) != 9:
                result['warnings'].append(f"Could not check for {file_path} presence, please report this. Output was: {responses[idx]}. Offending line seems to be: {line}")
                break
            if 'd' in item_info[1] or filename:
                module.fail_json(msg=f'{file_path} does not seem to be a file path.')
            else:
                filename = item_info[-1]
    return filename

def _get_file_md5(module, result, file_path):
    command = {'command': f'verify /md5 {file_path}'}
    responses = run_commands(module, command)
    for idx,response in enumerate(to_lines(responses)):
        for line in response:
            if line.startswith('verify /md5'):
                remote_md5 = line.split()[-1]
                return remote_md5
    result['warnings'].append(f"Could not parse device output to get MD5 hash of {file_path}, please report this. File will be skipped. Output was: {responses[idx]}. Offending line seems to be: {line}")
    return None

def list_files(module, result, file_path=None, directory_path=None, get_md5=False):
    files = []
    file_hashes = {}
    if directory_path:
        files.extend(_parse_directory(module, result, directory_path))
        if get_md5:
            for f in files:
                remote_md5 = _get_file_md5(module, result, f"{directory_path}/{f}")
                if not remote_md5:
                    # Skip this file if MD5 could not be retrieved.
                    continue
                file_hashes[f] = remote_md5
    if file_path:
        filename = _parse_file(module, result, file_path)
        files.append(filename)
        if get_md5:
            remote_md5 = _get_file_md5(module, result, f"{file_path}")
            if remote_md5:
                file_hashes[filename] = remote_md5
    if get_md5:
        result.update({'files': file_hashes})
    else:
        result.update({'files': files})

def verify_md5(module, result, file_path, md5):
    remote_md5 = _get_file_md5(module, result, file_path)
    if md5 != remote_md5:
        module.fail_json(msg=f'File {file_path} has wrong MD5 hash. Got {remote_md5}, expected {md5}')

def main():
    argument_spec = dict(
        file=dict(type='path'),
        directory=dict(type='path'),
        get_md5=dict(type='bool', default=False),
        expected_md5=dict(type='str'),
    )
    mutually_exclusive = [("expected_md5", "directory"), ("expected_md5", "get_md5")]
    module = AnsibleModule(
        argument_spec=argument_spec,
        mutually_exclusive=mutually_exclusive,
        supports_check_mode=False,
    )
    result = { "changed": False,
               "warnings": list() }

    if module.params["expected_md5"]:
        verify_md5(module, result, module.params["file"], module.params["expected_md5"])

    elif module.params["directory"] or module.params["file"]:
        list_files(module, result, file_path=module.params["file"],
                                   directory_path=module.params["directory"],
                                   get_md5=module.params["get_md5"])

    module.exit_json(**result)

if __name__ == "__main__":
    main()