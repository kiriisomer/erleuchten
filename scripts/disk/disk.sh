#!/bin/bash

START_TIME=30


function check_number_of_fields()
{
	if [ $2 -ne $1 ]; then
		echo "POWER/INTERFACE/DISK-ORDER wrong..."
		echo "$2 of fields detected (Expected: $1)"
		exit 2
	fi
	
	return 0
}


function check_rtn()
{
    if [ $1 -ne 0 ]; then
        echo "Last cmd failed"
        exit 2
    fi
    
	return 0
}


function check_md5()
{
	erleuchten-env sshcmd --name $1 --order 1 --cmd "md5sum /mnt/test/1001/test.txt | awk '{print \$1}' > /tmp/test.txt.md5"
	erleuchten-env sshcmd --name $1 --order 1 --cmd "md5sum /home/test2.txt | awk '{print \$1}' > /tmp/test2.txt.md5"
	erleuchten-env sshcmd --name $1 --order 1 --cmd "md5sum /etc/test3.txt | awk '{print \$1}' > /tmp/test3.txt.md5"

	erleuchten-env sshcmd --name $1 --order 1 --cmd "cmp /tmp/test.txt.md5 /tmp/test2.txt.md5" 
	check_rtn $?

	erleuchten-env sshcmd --name $1 --order 1 --cmd "cmp /tmp/test2.txt.md5 /tmp/test3.txt.md5"
	check_rtn $?
	
	return 0
}


echo "Start to read shells.conf-->>>"
# Try to find the order of VMs to perform disk-off
num_of_fields=`awk '$1 == "DISK-ORDER" {print NF - 1;}' ../shells.conf`
check_number_of_fields 3 $num_of_fields

VMs[0]=`awk '$1 == "DISK-ORDER" {print int($2);}' ../shells.conf`
VMs[1]=`awk '$1 == "DISK-ORDER" {print int($3);}' ../shells.conf`
VMs[2]=`awk '$1 == "DISK-ORDER" {print int($4);}' ../shells.conf`

for i in ${VMs[@]}; do
	if [ $i -ne "1" ] && [ $i -ne "2" ] && [ $i -ne "3" ]; then
		echo "Field content wrong"
		echo "$i detected (Expected: 1 OR 2 OR 3)"
		exit 2
	fi
done

# Find the time to stay disk-off
num_of_fields=`awk '$1 == "DISK-OFF" {print NF - 1;}' ../shells.conf`
check_number_of_fields 1 $num_of_fields

off_time=`awk '$1 == "DISK-OFF" {print int($2);}' ../shells.conf`

# Find the interval during each disk-off-then-on
num_of_fields=`awk '$1 == "DISK-OFF" {print NF - 1;}' ../shells.conf`
check_number_of_fields 1 $num_of_fields

wait_time=`awk '$1 == "DISK-INTERVAL" {print int($2);}' ../shells.conf`
echo "Done reading shells.conf---<<<"

echo "    The order is: ${VMs[@]}"
echo " The off-time is: $off_time"
echo "The wait-time is: $wait_time"
total_time=$[((off_time + START_TIME) * 2 + wait_time) * 3]
# total_time=`expr $off_time + $START_TIME`
# total_time=`expr $total_time + $wait_time`
# total_time=`expr $total_time \* 3`
echo "Total-time will be: $total_time"
# exit 0

ENV=$ERLEUCHTEN_ENVIRONMENT_NAME
# ENV=env02
erleuchten-env sshcmd --name $ENV --order 1 \
	--cmd "echo 'This is the file of disk-test' > /mnt/test/1001/test.txt"
erleuchten-env sshcmd --name $ENV --order 1 \
	--cmd "cp /mnt/test/1001/test.txt /home/test2.txt"
erleuchten-env sshcmd --name $ENV --order 1 \
	--cmd "cp /home/test2.txt /etc/test3.txt"
check_md5 $ENV

used_time=1
for (( tmp=0; tmp<=2;tmp++ )); do
	erleuchten-env detach-disk --name $ENV --order ${VMs[$tmp]} --tgt vda
	for((i=1; i<=$off_time; i++)); do
		echo "-->>$used_time/$total_time-Disk-Test-Order:${VMs[$tmp]}<<--"
		used_time=$[used_time + 1]
		sleep 1
	done

	erleuchten-env attach-disk --name $ENV --order ${VMs[$tmp]} \
		--src /home/images/vm1${VMs[$tmp]}_0001.qcow2 --tgt vda --fmt qcow2
	for((i=1; i<=$START_TIME; i++)); do
		echo "-->>$used_time/$total_time-Disk-Test-Order:${VMs[$tmp]}<<--"
		used_time=$[used_time + 1]
		sleep 1
	done
	check_md5 $ENV

	erleuchten-env detach-disk --name $ENV --order ${VMs[$tmp]} --tgt vdb
	for((i=1; i<=$off_time; i++)); do
		echo "-->>$used_time/$total_time-Disk-Test-Order:${VMs[$tmp]}<<--"
		used_time=$[used_time + 1]
		sleep 1
	done

	erleuchten-env attach-disk --name $ENV --order ${VMs[$tmp]} \
		--src /home/images/vm1${VMs[$tmp]}_0002.qcow2 --tgt vdb --fmt qcow2
	for((i=1; i<=$START_TIME; i++)); do
		echo "-->>$used_time/$total_time-Disk-Test-Order:${VMs[$tmp]}<<--"
		used_time=$[used_time + 1]
		sleep 1
	done
	check_md5 $ENV
	
	for((i=1; i<=$wait_time; i++)); do
		echo "-->>$used_time/$total_time-Disk-Test-Order:${VMs[$tmp]}<<--"
		used_time=$[used_time + 1]
		sleep 1
	done
done

echo "Successful"
