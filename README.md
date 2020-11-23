# ansible-download-os
Download a new OS from TFTP server using Ansible.

# Setup
Don't forget to install sshpass to use ssh connections with passwords.

```
apt-get install sshpass
```

# Host file

Allow Ansible to go to exec mode.

```
ansible_become = yes
ansible_become_method = enable
ansible_become_password = xxx
```

# Utilisation

```bash
ansible-playbook ios_get_new_update.yaml -i /path/to/host/file
```

# Demo
## Downloading the IOS
![Demo - IOS download](demo/gif_get_ios.gif)

