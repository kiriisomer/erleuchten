帮助你安装并运行vdbench，首先在本机的一个文件夹下面存放如下三个文件：
(1)paramfile.txt
(2)vdbench.tar
(3)run_vdbench.sh
然后,默认情况下会将前两个文件复制到远程机器上的路径，默认设置为：/home/Storage，你不需要去创建
这个目录，脚本会自动创建它。然后在目标机器上vdbench.tar会被解压到当前路径，最后运行vdbench测
试（vdbench -t和vdbench -f paramfile.txt）。
使用方法：sh run_vdbench.sh