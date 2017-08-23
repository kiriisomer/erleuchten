# 删除原来的，开始全新测试
virsh destroy vm11
virsh destroy vm12
virsh destroy vm13
virsh undefine vm11
virsh undefine vm12
virsh undefine vm13

rm -rf /home/images/vm*.*
ls -alh /home/images
virsh list --all

env_name="env02"

# 源虚拟机的名字，新生成的虚拟机会复制此虚拟机的3个磁盘
source_vm="cent7"

VMs[0]="vm11"
VMs[1]="vm12"
VMs[2]="vm13"

manage_dns="114.114.114.114"
manage_gateway="192.168.10.254"

manage_ips[0]="192.168.10.224"
manage_ips[1]="192.168.10.225"
manage_ips[2]="192.168.10.226"

# 这些网卡会被挂载到主机的特定网桥上，所以和那个网桥应该在一个网段
storage_ips[0]="10.11.12.224"
storage_ips[1]="10.11.12.225"
storage_ips[2]="10.11.12.226"

manage_names[0]="manageif1"
manage_names[1]="manageif2"
manage_names[2]="manageif3"

storage_names[0]="storageif1"
storage_names[1]="storageif2"
storage_names[2]="storageif3"


# 定义Env
erleuchten-env create --name $env_name

# 定义Env中的虚拟机
for ((i=0; i < 3; i++)); do
	erleuchten-env define-vm --name $env_name --vm-name ${VMs[$i]} \
        --vm-src-name $source_vm \
        --manage-ifcfg-source /etc/sysconfig/network-scripts/ifcfg-eth0  \
		--manage-if-name ${manage_names[$i]} --manage-addr ${manage_ips[$i]} \
        --manage-gateway $manage_gateway \
		--manage-mask 255.255.255.0 --manage-dns $manage_dns \
        --storage-ifcfg-source /etc/sysconfig/network-scripts/ifcfg-eth1 \
		--storage-if-name ${storage_names[$i]} --storage-addr ${storage_ips[$i]} \
		--storage-mask 255.255.255.0 \
		--ssh-user root --ssh-password 111111
done

# 定义需要用到的script
erleuchten-script create --name installStorage --script-path installStorage/installStorage.sh \
	--appendix-path installStorage/install_without_prompt.py installStorage/clis_1.2.84.pkg \
	installStorage/Storage_1.2.84_Alpha.pkg installStorage/QuickInstall.sh

erleuchten-script create --name runVdbench --script-path vdbench/run_vdbench.sh \
	--appendix-path vdbench/paramfile.txt vdbench/vdbench.tar

erleuchten-script create --name testPower --script-path power/power.sh

erleuchten-script create --name testDisk --script-path disk/disk.sh

erleuchten-script create --name testInterface --script-path interface/interface.sh

# 定义需要用到的script-set
erleuchten-script-set create --name yss01 --script-name installStorage

erleuchten-script-set create --name yss02 --script-name runVdbench

erleuchten-script-set create --name yss03 --script-name testPower

erleuchten-script-set create --name yss04 --script-name testDisk

erleuchten-script-set create --name yss05 --script-name testInterface

# 定义需要用到的testcase
erleuchten-testcase create --name ytc01 --env-name $env_name --init-scriptset yss01 \
	--test-scriptset yss02 yss03 yss04 yss05

erleuchten-testcase set-scriptset-prop --name ytc01 --scriptset yss02 --background 1

# 初始化testcase
erleuchten-testcase init --name ytc01

# 开始testcase
cp shells.conf /home/erleuchten/testscript/
erleuchten-testcase start --name ytc01
