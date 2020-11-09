# ansible-download-os
Download a new OS from TFTP server using Ansible.

# Setup
Don't forget to install sshpass to use ssh connections with passwords.

```
apt-get install sshpass
```

# Demo
## Downloading the IOS
![Demo - IOS download](demo/gif_get_ios.gif)

## Deleting the IOS
![Demo - IOS delete](demo/gif_delete_ios.gif)

# Host file

Allow Ansible to go to exec mode.

```
ansible_become = yes
ansible_become_method = enable
ansible_become_password = xxx
```