# ansible-download-os

Upload a new OS to Cisco IOS devices via SCP using Ansible.

This repository contains 2 small Ansible modules to manipulate [files](library/ios_file.py) and [directories](library/ios_directory.py) on IOS devices.

The Ansible role [copy_scp](roles/copy_scp) will upload files to IOS devices using SCP. In the role variables, file bundles are specified.
It does the following:
- Creates required remote directories on the IOS devices
- Check if the files are already present on the devices using MD5 hashes
- Check if the device has enough free space
- Copy the missing files to the devices using SCP
- Verify the copied files using MD5 hashes

# Setup

```
pip install -r requirements.txt
```

# Usage

``` bash
ansible-playbook -i inventory.yml copy-os-ios.yml
```

# Configuration

## Inventory

An inventory file can be provided with the above command, using the `-i` option. Inventory files will contain information about the devices, such as the credentials and IP addresses. A template has been provided [here](inventory.yml).

## Ansible role configuration

1. Put the files you want to upload to the `roles/copy_scp/files` directory
2. Update [the role variables](roles/copy_scp/vars/main.yml). This is where you define the file bundles.
    - `fiilename`: the filename (locally and on the remote devices)
    - `local_dir`: local directory where the file is located
    - `remote_dir`: remote directry where the file should be copied
    - `md5_hash`: the file MD5 hash
    - `size`: the file size in kB
3. Ensure the [playbook](copy-os-ios.yml) uses the correct bundle name.

## Ansible global configuration

Eventually create a `ansible.cfg` file in the Ansible working directory to specify any Python virtual envirnement or disable SSH host key check.

``` ini
[defaults]
host_key_checking = False
interpreter_python = venv/bin/python
```

# Demo
## Downloading the IOS
![Demo - IOS download](demo/ios_copy_scp.gif)

