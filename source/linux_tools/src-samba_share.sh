apt-get install samba
mkdir /smbshare
chmod 777 /smbshare -R
cp /etc/samba/smb.conf /etc/samba/smb.conf.bak
vi /etc/samba/smb.conf
######在smb.conf文件最后增加如下内容###########
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
##############################################

touch /etc/samba/smbpasswd
useradd smbuser1
smbpasswd -a smbuser1
cd /smbshare/
