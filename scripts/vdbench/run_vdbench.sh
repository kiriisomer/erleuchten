#!/bin/bash

LOCAL_PATH=$PWD
REMOTE_PATH="/home/Storage"
ENV=$ERLEUCHTEN_ENVIRONMENT_NAME

#0 install java
erleuchten-env sshcmd --name $ENV --order 1 --cmd "yum -y install java"

# 1. copy file to the path on the remote vm
erleuchten-env sshput --name $ENV --order 1 --dst $REMOTE_PATH \
    --src $LOCAL_PATH/vdbench.tar
erleuchten-env sshput --name $ENV --order 1 --dst $REMOTE_PATH \
    --src $LOCAL_PATH/paramfile.txt

# 2. unzip the file
erleuchten-env sshcmd --name $ENV --order 1 --cmd "tar -xvf $REMOTE_PATH/vdbench.tar \
    -C $REMOTE_PATH"
erleuchten-env sshcmd --name $ENV --order 1 --cmd "chmod +x $REMOTE_PATH/vdbench/vdbench"
erleuchten-env sshcmd --name $ENV --order 1 --cmd "$REMOTE_PATH/vdbench/vdbench -t"

# 3. run vdbench according to the paramfile
erleuchten-env sshcmd --name $ENV --order 1 --cmd "$REMOTE_PATH/vdbench/vdbench \
    -f $REMOTE_PATH/paramfile.txt"
