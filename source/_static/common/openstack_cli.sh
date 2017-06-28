#keystone user-create --name demo --tenant csq --pass demo --email demo@cecgw.cn
##keystone user-role-add --user=demo --tenant=csq --role=_member_
#
## 创建租户
#keystone user-create --name demo --tenant csq --pass demo --email demo@cecgw.cn
## 创建租户用户
#keystone user-role-add --user=demo --tenant=csq --role=system_tenant
#
#neutron net-create ext-net --provider:network_type vxlan --provider:segmentation_id 5000
#
#neutron net-create ext-net --provider:network_type vlan  --provider:physical_network physnet1 --provider:segmentation_id 32 --tenant-id <tenant-id>
#neutron subnet-create ext-net 10.192.32.0/24 --gateway_ip 10.192.32.254 --dns_nameservers list=true 114.114.114.114 8.8.8.8 --tenant-id <tenant-id>
#
#
#
#
#$ tenant=$(keystone tenant-list | awk '/service/ {print $2}')
#$ neutron router-create router01
#$ neutron net-create --tenant-id $tenant public01 --provider:network_type flat --provider:physical_network physnet1 --router:external True
#$ neutron subnet-create --tenant-id $tenant --name public01_subnet01 --gateway 10.64.201.254 public01 10.64.201.0/24 --disable-dhcp
#$ neutron router-gateway-set router01 public01
#
#
#neutron net-create ext-net --shared --router:external=True --provider:network_type vxlan --provider:segmentation_id 5000
#
## Create networks
#neutron net-create --shared \
#                   --router:external=True \
#                   --provider:physical_network vlan \
#                   --provider:network_type vlan \
#                   --provider:segmentation_id 1100 \
#                   "GATEWAY_NET_V6"
# 
#neutron subnet-create --dns-nameserver '8.8.8.8' \
#                      --dns-nameserver '8.8.4.4' \
#                      --name "GATEWAY_SUBNET_V6V4" \
#                      "GATEWAY_NET_V6" \
#                      '10.51.50.0/16'
# 
#neutron subnet-create --ip-version=6 \
#                      --ipv6-address-mode=dhcpv6-stateless \
#                      --dns-nameserver '2001:4860:4860::8888' \
#                      --dns-nameserver '2001:4860:4860::8844' \
#                      --name "GATEWAY_SUBNET_V6V6" \
#                      "GATEWAY_NET_V6" \
#                     '2001:4800:1ae1:18::0/64'

# 使用admin 身份
source /root/openstackrc

# 创建租户
keystone tenant-create --name csq --description "csq tenant"
# 创建租户用户
keystone user-create --name demo2 --tenant csq --pass demo --email demo@cecgw.cn
keystone user-role-add --user=demo2 --tenant=csq --role=system_tenant

#keystone user-delete chensq

# 创建外部网络
neutron net-create ext-net --shared --router:external=True --provider:network_type vxlan --provider:segmentation_id 5000
# 创建外网子网
neutron subnet-create ext-net 192.168.159.0/24 --name ext-subnet --allocation-pool start=192.168.159.201,end=192.168.159.210 --gateway 192.168.159.2 --dns-nameserver 114.114.114.114

source /smbshare/chensqrc
# 创建租户网络
neutron net-create demo-net
neutron subnet-create demo-net 10.10.10.0/24 --name demo-subnet --allocation-pool start=10.10.10.2,end=10.10.10.254 --gateway 10.10.10.1 --dns-nameserver 114.114.114.114
# 创建路由，设置外网网关，内网接口！
neutron router-create demo-router --distributed False
neutron router-gateway-set demo-router ext-net
neutron router-interface-add demo-router demo-subnet