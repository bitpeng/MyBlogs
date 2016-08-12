#!/bin/bash

set -x

apt-get install samba

if [ ! -d /smbshare ];then
    mkdir /smbshare
fi
chmod 777 /smbshare

if [ ! -e /etc/samba/smb.conf.bak ];then
    cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
fi

if grep -Fxq "# add by chenshiqiang" /etc/samba/smb.conf; then
    :
else
    cat << EOF >> /etc/samba/smb.conf
# add by chenshiqiang
security = user
username map = /etc/samba/users

[smbshare]
path=/smbshare
available=yes
browseable=yes
public=yes
valid users = smbuser1

writeable=yes
EOF
fi


touch /etc/samba/smbpasswd
useradd smbuser1
smbpasswd -a smbuser1
cd /smbshare/
/etc/init.d/samba restart
