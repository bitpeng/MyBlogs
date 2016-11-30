#! /usr/bin/env bash

error_log='/smbshare/os_status.log'
if [[ ! -e $error_log ]];then
    touch $error_log
fi

source /root/openstackrc
set -ex

nova service-list
cinder service-list
neutron agent-list

set +ex

echo -e "\n" && sleep 2

# 检查glance 服务是否启动
# 后面睡眠两秒是保证结果在终端顺序输出，否则可能会交织在一起！
echo -e "\e[1;31m++ check glance service status \e[0m"
ps -ef | grep glance | grep -v grep
echo
netstat -pltn | grep 9292
echo -e "\n" && sleep 2

# 检查keystone 服务是否启动
echo -e "\e[1;31m++ check keystone service status \e[0m"
ps -ef | grep keystone | grep -v grep
echo
netstat -pltn | grep 5000
echo -e "\n" && sleep 2

#swift stat

cd /usr/bin
##ser=`for com in cinder glance nova keystone heat ceilometer neutron; do for i in $com-*; do [[ ! $i =~ "bak" ]] && service $i status; done; done 2>/dev/null | grep process | awk '{print $1}'`
#ser=`for com in cinder glance nova keystone neutron; do for i in $com-*; do [[ ! $i =~ "bak" ]] && service $i status; done; done 2>/dev/null | awk '{print $1}'`
#for i in $ser; do service $i status; done

echo -e "\e[1;31m++ check recognized binary service status \e[0m"
echo "" > $error_log
for com in nova cinder neutron glance keystone heat ceilometer;
do
    #for i in $com*; do [[ ! $i =~ "bak" ]] && service $i status 2>/dev/null; done
    for i in $com*; do [[ ! $i =~ "bak" ]] && service $i status 2>>$error_log; done
    echo
done #2>/dev/null
#echo -e "\n" && sleep 2
echo && sleep 2

echo -e "\e[1;31m++ check rabbitmq-server status \e[0m"
set -ex
rabbitmqctl status
