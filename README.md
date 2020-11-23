# ansible-download-os
Download a new OS from TFTP server using Ansible.

# Setup
Don't forget to install sshpass to use ssh connections with passwords.

```
pip install -r requirements.txt
apt-get install sshpass
```

# Utilisation

```bash
ansible-playbook ios_get_new_update.yaml -i /path/to/host/file
```

# Host file

A host file can be provided with the above command, using the `-i` command. Host file will contain information about the device, such as the credentials and IP address. A template has been provided in the `./testbed/hosts` folder.

## Special configuration

Allow Ansible to go to exec mode.

```
ansible_become = yes
ansible_become_method = enable
ansible_become_password = xxx
```

# Demo
## Downloading the IOS
![Demo - IOS download](demo/gif_get_ios.gif)

