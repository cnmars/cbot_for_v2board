#!/bin/bash

# 检测root权限
[[ $EUID -ne 0 ]] && echo -e "必须使用root用户运行此脚本..." && exit 1
echo -e "root权限检测通过..."

# 检测系统版本
if [[ -f /etc/redhat-release ]]; then
    release="centos"
elif cat /etc/issue | grep -Eqi "debian"; then
    release="debian"
elif cat /etc/issue | grep -Eqi "ubuntu"; then
    release="ubuntu"
elif cat /etc/issue | grep -Eqi "centos|red hat|redhat"; then
    release="centos"
elif cat /proc/version | grep -Eqi "debian"; then
    release="debian"
elif cat /proc/version | grep -Eqi "ubuntu"; then
    release="ubuntu"
elif cat /proc/version | grep -Eqi "centos|red hat|redhat"; then
    release="centos"
else
    echo -e "未检测到系统版本..." && exit 1
fi

function is_cmd_exist() {
    local cmd="$1"
    if [ -z "$cmd" ]; then
        return 1
    fi

    which "$cmd" > /dev/null 2>&1
    if [ $? -eq 0 ]; then
        return 0
    fi
	  return 2
}

install_base() {
    if [[ x"${release}" == x"centos" ]]; then
        yum update -y
        yum install epel-release -y
        yum install wget curl tar crontabs sort gcc zlib-devel libffi-devel openssl-devel bzip2-devel  -y
    else
        apt update -y
        apt install wget curl tar cron git -y
    fi
}

# 安装Python
install_python() {
    echo -e "检测python版本..."
    python_version=$(python3 -c 'import sys; print(".".join(map(str, sys.version_info[:3])))' 2>/dev/null)
    if [[ -z $python_version ]]; then
        python_version="0.0.0"
    fi
    echo -e "当前python版本: $python_version"
    required_version="3.8.0"
    download_version="3.10.10"
    extracted_version="${download_version%.*}"

    # 将版本号转换为数字，并进行比较
    if [[ "$(printf '%s\n' "$python_version" "$required_version" | sort -V | head -n1)" == "$required_version" ]]; then
        echo "Python版本满足要求..."
    else
        echo -e "python版本不满足要求,开始安装python..."
        if [[ x"${release}" == x"centos" ]]; then
            # 下载并安装Python
            temp_dir=$(mktemp -d)
            cd "$temp_dir"
            wget https://www.python.org/ftp/python/$download_version/Python-$download_version.tgz
            tar -xf Python-$download_version.tgz
            make clean
            cd Python-$download_version
            ./configure --enable-optimizations
            make -j$(nproc)
            make altinstall

            # 清理临时文件
            cd ~
            rm -rf "$temp_dir"

            # 创建新的pip3和python3软链接
            unlink /usr/bin/pip3 > /dev/null 2>&1
            ln -s /usr/local/bin/pip$extracted_version /usr/bin/pip3
            unlink /usr/bin/python3 > /dev/null 2>&1
            ln -s /usr/local/bin/python$extracted_version /usr/bin/python3
            
            python3 -V
            pip3 -V
            echo -e "python${extracted_version} 安装成功"
        else
            sudo apt update && sudo apt install python3 python3-pip -y
        fi
    fi
}


install_cbot(){
    pip3 install python-telegram-bot --upgrade

    cd /usr/local/
    git clone https://github.com/caoyyds/cbot_for_v2board.git
    cd cbot_for_v2board
    cp cbot_for_v2board.service /etc/systemd/system/

    systemctl daemon-reload
    systemctl enable cbot_for_v2board.service

    cd /usr/local/cbot_for_v2board/conf
    mv config config.conf

    echo "安装完成..."
    echo "------------------------------------------"
    echo "请修改配置文件："
    echo "vi /usr/local/cbot_for_v2board/conf/config.conf"
    echo "启动Bot命令:"
    echo "systemctl start cbot_for_v2board.service"
    echo "停止Bot命令:"
    echo "systemctl stop cbot_for_v2board.service"
    echo "重启Bot命令:"
    echo "systemctl restart cbot_for_v2board.service"
    echo "------------------------------------------"
}

is_cmd_exist "systemctl"
if [[ $? != 0 ]]; then
    echo "systemctl 命令不存在，请使用较新版本的系统，例如 Ubuntu 18+、Debian 9+"
    exit 1
fi

install_base
install_python
install_cbot

