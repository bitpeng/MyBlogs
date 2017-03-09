#REQ: curl -i 'http://100.100.100.254:5000/v2.0/tokens' -X POST -H "Accept: application/json" -H "Content-Type: application/json" -H "User-Agent: python-novaclient" -d '{"auth": {"tenantName": "csq", "passwordCredentials": {"username": "chensq", "password": "{SHA1}c60f964054e2080b1c827fae07ef0e5d92d2d285"}}}'



#token_json=`curl -d '{"auth": {"tenantName": "csq", "passwordCredentials": {"username": "chensq", "password": "cec123"}}}' -H "Content-type: application/json" http://localhost:5000/v2.0/tokens | python -m json.tool`


#########################################################

#source /root/openstackrc
source /smbshare/chensqrc

# 获取租户id
tenant_id=`keystone tenant-list | grep $OS_TENANT_NAME | grep -v invisible* | awk '{print $2}'`

# 获取json格式的token信息！
token_json=`curl -d "{\"auth\": {\"tenantName\": \"$OS_TENANT_NAME\", \"passwordCredentials\": {\"username\": \"$OS_USERNAME\", \"password\": \"$OS_PASSWORD\"}}}" -H "Content-type: application/json" http://localhost:5000/v2.0/tokens | python -m json.tool`

# token id值
token_id=`echo $token_json | python -c "import sys, json; tok = json.loads(sys.stdin.read()); print tok['access']['token']['id'];"`

# 获取租户虚拟机列表，详细信息！
curl -i "http://100.100.100.254:8774/v2/$tenant_id/servers/detail" -X GET -H "Accept: application/json" -H "User-Agent: python-novaclient" -H "X-Auth-Project-Id: $OS_TENANT_NAME" -H "X-Auth-Token:$token_id"

# 获取租户虚拟机简要信息！
curl  "http://100.100.100.254:8774/v2/$tenant_id/servers" -X GET -H "Accept: application/json" -H "User-Agent: python-novaclient" -H "X-Auth-Project-Id: $OS_TENANT_NAME" -H "X-Auth-Token:$token_id" | python -m json.tool

# 获取租户某个虚拟机的id
a_instance_id=`curl  "http://100.100.100.254:8774/v2/$tenant_id/servers" -X GET -H "Accept: application/json" -H "User-Agent: python-novaclient" -H "X-Auth-Project-Id: $OS_TENANT_NAME" -H "X-Auth-Token:$token_id" | python -c "import sys, json; ser = json.loads(sys.stdin.read()); print ser['servers'][0]['id'];"`

# 获取某个虚拟机的详细信息
curl  "http://100.100.100.254:8774/v2/$tenant_id/servers/$a_instance_id" -X GET -H "Accept: application/json" -H "User-Agent: python-novaclient" -H "X-Auth-Project-Id: $OS_TENANT_NAME" -H "X-Auth-Token:$token_id" 


###############################################################

# 获取neutron版本信息
curl -i -X GET http://10.10.10.10:9696/ -H "User-Agent: python-neutronclient" -H "X-Auth-Token: $token_id"


#curl  "http://100.100.100.254:8774/v2/$tenant_id/servers/06419e7c-762c-41d7-89ad-a5956ff4deb3" -X GET -H "Accept: application/json" -H "User-Agent: python-novaclient" -H "X-Auth-Project-Id: $OS_TENANT_NAME" -H "X-Auth-Token:$token_id" 
