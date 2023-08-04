#!/bin/bash

# 检测root权限
[[ $EUID -ne 0 ]] && echo -e "${red}错误： 必须使用root用户运行此脚本!\n" && exit 1
echo -e "root权限检测通过..."

# 检查Linux系统版本
if [ -f /etc/os-release ]; then
    . /etc/os-release
    OS=$ID
    VERSION=$VERSION_ID
else
    echo "无法确定Linux发行版..."
    exit 1
fi

# 检查是否为CentOS
if [ "$OS" != "centos" ]; then
    echo "该脚本仅适用于CentOS..."
    exit 1
fi

echo "检测到CentOS $VERSION 继续执行安装..."

# 安装基础软件
install_base() {
    echo -e "开始安装基础包..."
    yum update -y
    yum install epel-release -y
    yum install wget curl tar crontabs sort gcc zlib-devel libffi-devel openssl-devel bzip2-devel  -y
    echo -e "基础包安装成功..."
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
    fi
}

install_base
install_python

