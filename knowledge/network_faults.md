# 网络故障排查知识库

## 故障1：OSPF 邻居无法建立

现象：display ospf peer brief 看不到邻居，或邻居停留在 Init/ExStart 状态。

排查步骤：
1. ping 对端直连 IP，确认物理层与 IP 连通。
2. display ospf brief 检查两端区域号是否一致。
3. 检查两端 Router-ID 是否冲突。
4. 检查 Hello/Dead 计时器与区域类型是否一致。
5. 检查接口是否通过 network 正确宣告进 OSPF。

相关命令：
display ospf peer brief
display ospf interface GigabitEthernet0/0/1
ospf 1 router-id 1.1.1.1
 area 0
 network 192.168.1.0 0.0.0.255

## 故障2：VRRP 出现双主（两台都是 Master）

现象：display vrrp brief 显示两台设备状态都是 Master。

排查步骤：
1. 双主通常是 Backup 收不到 Master 通告，先检查 VRRP 组之间二层连通性。
2. 检查中间 Trunk 链路是否放行该 VLAN：display port vlan。
3. 检查两端 VRID 与虚拟 IP 是否一致。
4. 若配置认证，检查两端认证方式与密码是否一致。

相关命令：
display vrrp brief
display port vlan
interface Vlanif10
 vrrp vrid 1 virtual-ip 192.168.10.1

## 故障3：VLAN 内主机无法互通

现象：同一 VLAN 两台主机 ping 不通。

排查步骤：
1. display vlan 检查接入口是否划入正确 VLAN。
2. display port vlan 检查 Trunk 是否放行该 VLAN。
3. 检查主机 IP、掩码、网关配置。
4. 检查是否存在端口隔离、MUX VLAN 等策略阻断。

相关命令：
display vlan
interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 10

## 故障4：SSH 无法登录设备

现象：SSH 连接被拒绝或超时。

排查步骤：
1. ping 设备管理 IP，确认连通性。
2. 检查 stelnet server enable 是否开启。
3. 检查 AAA 用户 service-type 是否包含 ssh、权限级别是否为 15。
4. 检查 VTY 下 protocol inbound ssh 与 authentication-mode aaa。

相关命令：
stelnet server enable
display ssh server status
aaa
 local-user admin service-type ssh
user-interface vty 0 4
 authentication-mode aaa
 protocol inbound ssh

## 故障5：Eth-Trunk 链路聚合不通或成员口不选中

现象：display eth-trunk 显示成员口为 Unselected，或聚合链路不通、流量不均衡。

排查步骤：
1. 检查两端聚合模式是否一致（手工负载分担 mode manual 或静态 LACP mode lacp-static）。
2. 检查成员口速率、双工模式是否一致。
3. 成员口下不能单独配置 IP，接口类型与加入的 VLAN 必须一致。
4. LACP 模式下检查活动链路数上限、least active-linknumber 阈值。
5. 确认成员口物理状态均为 Up，未被 shutdown。

相关命令：
display eth-trunk
interface Eth-Trunk1
 mode lacp-static
 trunkport GigabitEthernet0/0/1
 least active-linknumber 1

## 故障6：二层环路导致广播风暴

现象：全网卡顿、交换机指示灯高速狂闪、CPU 占用高、出现 MAC 地址漂移告警。

排查步骤：
1. display mac-address 查看 MAC 漂移告警，定位环路发生的 VLAN 和端口。
2. 检查网络中是否存在冗余链路而未启用 STP。
3. display stp brief 检查端口角色（Root/Designated/Alternate）与状态。
4. 接终端的端口配置为边缘端口并开启 BPDU 保护。
5. 必要时开启环路检测与风暴控制。

相关命令：
display stp brief
stp mode mstp
interface GigabitEthernet0/0/10
 stp edged-port enable
loopback-detect enable
storm-control broadcast min-rate 100 max-rate 200

## 故障7：NAT 不生效，内网无法访问外网

现象：内网主机无法访问公网，出口路由器未做地址转换。

排查步骤：
1. display nat session all 查看是否产生 NAT 转换表项。
2. 检查 ACL 是否正确匹配内网网段。
3. 检查 nat outbound 是否配置在连接运营商的正确出接口上。
4. 检查是否配置了指向公网的默认路由，出接口状态是否 Up。
5. 确认运营商线路与 DNS 正常。

相关命令：
display nat session all
acl 2000
 rule permit source 192.168.1.0 0.0.0.255
interface GigabitEthernet0/0/0
 nat outbound 2000
ip route-static 0.0.0.0 0.0.0.0 下一跳IP

## 故障8：DHCP 客户端获取不到 IP 地址

现象：客户端网卡自动获得 169.254.x.x 私有地址，提示网络受限。

排查步骤：
1. 全局是否执行 dhcp enable。
2. 检查地址池 network、gateway-list、dns-list、lease 配置。
3. 检查 VLANIF 接口下是 dhcp select global 还是 interface，与建池方式是否匹配。
4. 跨网段获取时检查 dhcp select relay 与 dhcp relay server-ip。
5. display ip pool 查看地址池是否耗尽、接口是否属于正确 VLAN。

相关命令：
dhcp enable
ip pool vlan10
 network 192.168.10.0 mask 255.255.255.0
 gateway-list 192.168.10.254
 dns-list 8.8.8.8
interface Vlanif10
 dhcp select global
display ip pool name vlan10 used

## 故障9：Telnet 无法登录设备

现象：Telnet 连接被拒绝或提示协议不允许。

排查步骤：
1. 检查 telnet server enable 是否开启。
2. 检查 VTY 下 protocol inbound 是否允许 telnet（或 all）。
3. 检查认证方式（aaa 或 password）与用户密码。
4. 检查 VTY 是否绑定了限制访问的 ACL。

相关命令：
telnet server enable
aaa
 local-user admin password cipher Admin@123
 local-user admin service-type telnet
 local-user admin privilege level 15
user-interface vty 0 4
 authentication-mode aaa
 protocol inbound telnet

## 故障10：跨交换机 Trunk 链路 VLAN 不通

现象：同一 VLAN 跨交换机的主机无法互通。

排查步骤：
1. 两端互联口是否都配置为 port link-type trunk。
2. display port vlan 检查 Trunk 是否放行对应 VLAN（默认只放行 VLAN 1）。
3. 检查两端 Trunk 的 PVID 是否一致，是否误把业务 VLAN 设成 PVID。
4. 检查互联接口是否 Up、是否被聚合或安全策略影响。

相关命令：
display port vlan
interface GigabitEthernet0/0/24
 port link-type trunk
 port trunk allow-pass vlan 10 20
 port trunk pvid vlan 1

## 故障11：VLANIF 三层接口状态为 Down

现象：display interface Vlanif 显示接口协议 Down，网关无法 ping 通。

排查步骤：
1. VLANIF 对应的 VLAN 内必须存在 Up 的物理接口（有 Access 口加入该 VLAN，或 Trunk 放行且对端有设备）。
2. display vlan 检查该 VLAN 下是否有活跃成员口。
3. 检查成员口是否被 shutdown、线缆是否正常。
4. 检查 VLANIF 是否配置了 IP 且未被手工 shutdown。

相关命令：
display interface Vlanif10
display vlan 10
interface GigabitEthernet0/0/1
 port link-type access
 port default vlan 10
 undo shutdown

## 故障12：静态路由不生效

现象：已配置 ip route-static，但路由表中没有该路由或流量不通。

排查步骤：
1. display ip routing-table 查看静态路由是否真正下发。
2. 检查下一跳是否直连可达、出接口是否 Up。
3. 检查目的网段与掩码（前缀长度）是否写错。
4. 检查是否有更优优先级的路由覆盖了静态路由。
5. 对端设备是否配置了回程路由。

相关命令：
display ip routing-table
display ip routing-table protocol static
ip route-static 192.168.2.0 255.255.255.0 192.168.1.1
tracert 192.168.2.1

## 故障13：ACL 策略不生效

现象：配置了 ACL 或 traffic-filter，但流量没有被拦截或放行。

排查步骤：
1. 确认 ACL 是否正确应用到接口，方向 inbound/outbound 是否选反。
2. 检查 rule 的匹配顺序（按编号顺序匹配），是否有前置规则命中。
3. 检查通配符掩码（反掩码）是否正确，如 0.0.0.255。
4. display acl all 查看规则命中计数，确认是否有流量匹配。
5. 区分 ACL 是被 traffic-filter 引用还是被 NAT、Telnet 等引用。

相关命令：
acl 3000
 rule deny ip source 192.168.1.0 0.0.0.255 destination 10.0.0.0 0.0.0.255
interface GigabitEthernet0/0/1
 traffic-filter inbound acl 3000
display acl 3000

## 故障14：OSPF 邻居 Full 但学不到路由

现象：display ospf peer 显示邻居 Full，但路由表中没有对端网段。

排查步骤：
1. 检查对端网段是否通过 network 宣告进 OSPF。
2. 检查接口是否被配置为 silent-interface（被动接口只收不发或不建邻）。
3. 检查区域类型（Stub/NSSA）与 ABR 是否正确下发区域间路由。
4. 检查两端接口掩码是否一致（广播/NBMA 网络要求一致）。
5. display ospf lsdb 查看 LSA 是否生成。

相关命令：
display ospf routing
display ospf interface
display ospf lsdb
ospf 1
 silent-interface GigabitEthernet0/0/10

## 故障15：接口被 error-down 自动关闭

现象：接口物理状态变为 down，日志提示 ERROR-DOWN，接入业务中断。

排查步骤：
1. 查看日志确认触发原因，常见为 BPDU 保护、端口安全、链路聚合成员属性不一致、环路检测。
2. display interface 查看接口是否处于 error-down 状态。
3. 定位并消除触发原因（如误接交换机到边缘端口、聚合成员口配置不一致）。
4. 可配置 error-down 自动恢复，或手工 undo shutdown 恢复。

相关命令：
display interface GigabitEthernet0/0/1
display error-down recovery
error-down auto-recovery cause bpdu-protection interval 30
interface GigabitEthernet0/0/1
 undo shutdown

## 故障16：同网段主机 ping 不通但配置看似正常

现象：IP、掩码、VLAN 都已配置，同网段主机仍然无法互通。

排查步骤：
1. 关闭主机防火墙（Windows 防火墙默认可能禁止 ICMP）。
2. display arp 检查是否解析到对端 MAC，排查 ARP 学习失败或 IP 地址冲突。
3. 检查两端接入口是否在同一 VLAN，端口隔离/端口安全是否阻断。
4. 检查是否存在 MAC 地址限制、静态 MAC 绑定。
5. 检查主机网关与子网掩码是否一致。

相关命令：
ping 192.168.10.2
display arp
display mac-address
display port-isolate group 1
