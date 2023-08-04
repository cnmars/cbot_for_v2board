#!/bin/bash

# 检查是否使用root用户运行脚本
if [[ $EUID -ne 0 ]]; then
  echo -e "必须使用root用户运行此脚本..."
  exit 1
fi

echo -e "root权限检测通过..."

# 检查是否安装了cbot_for_v2board
install_dir="/usr/local/cbot_for_v2board"
if [ ! -d "$install_dir" ]; then
  echo "没有检查到cbot_for_v2board安装目录 请检查是否安装过cbot_for_v2board"
  exit 1
fi

# 进入安装目录
cd "$install_dir"

# 检查是否使用git部署
if [ ! -d ".git" ]; then
  echo "必须使用git部署才能使用此脚本更新..."
  exit 1
fi

# 检查是否安装了git
if ! command -v git &> /dev/null; then
    echo "没有检查到git命令 请先安装git"
    exit 1
fi

# 更新cbot_for_v2board
echo "正在更新cbot_for_v2board..."
git config --global --add safe.directory "$(pwd)"
git fetch --all && git reset --hard origin/main && git pull origin main

# 重启cbot_for_v2board
echo "正在重启cbot_for_v2board..."
systemctl restart cbot_for_v2board.service

echo "cbot_for_v2board更新成功..."
