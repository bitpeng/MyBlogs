#!/bin/bash
ceph auth get-key client.cinder | tee client.cinder.key
UUID=`uuidgen`
echo $UUID
cat > secret.xml <<EOF
<secret ephemeral='no' private='no'>
  <uuid>${UUID}</uuid>
  <usage type='ceph'>
    <name>client.cinder secret</name>
  </usage>
</secret>
EOF
virsh secret-define --file secret.xml
virsh secret-set-value --secret ${UUID} --base64 $(cat client.cinder.key)
virsh secret-list
cd /usr/bin/
for i in nova*;do service $i restart ;done
