# openstack 部署要点

tags： OpenStack

---



allione方式：
要点，
lvm作存储：
raid，raid1一块，raid5 2块；
ceph作存储：
raid1一块，其他的raid0；


## allinone方式

### 存储：

* v2.3版本lvm作存储，raid1一块(操作系统安装盘)，其他的作raid5；v2.5 ceph作存储，raid1一块，其他的raid0；
* ceph内部尽量使用内部网络IP，不要用外网ip；
* v2.5 镜像格式只能使用raw格式，因为ceph作后端存储;

