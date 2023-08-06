# Cbot

小C-TelegramBot  
为v2board开发的群组小游戏及实用功能机器人

## 介绍

- 每日签到
- 通过Bot更改密码
- 个人信息查询
- 群组流量小游戏
  - 老虎机
  - 骰子(开发中...)
- 群组红包小游戏
  - 流量红包
  - 余额红包(开发中...)
  
## 安装

> 依赖关系:  
> Bot运行需要python3.8及以上版本  
> 安装脚本会尝试安装python3.8及以上版本  
> 如果安装失败请自行安装python3.8及以上版本  

- 安装脚本

  ```bash
  bash <(curl -Ls https://raw.githubusercontent.com/caoyyds/cbot_for_v2board/main/install_cbot.sh)
  ```

## 更新

```bash
bash <(curl -Ls https://raw.githubusercontent.com/caoyyds/cbot_for_v2board/main/update_cbot.sh)
```

## 使用

- 配置文件

  >[Database]  
  >host = 127.0.0.1  
  >user = user  
  >pwd = pwd  
  >db = dbname  
  >  
  >[Telegram]  
  >cbot_for_v2board = token  
  >group_username = @group_username  
  >group_url = group_url  
  >  
  >[V2board]  
  >name = v2board_name  
  >url = v2board_url  

  - Database项  
    数据库配置，填写v2board数据库信息

  - Telegram项  
    机器人token可以通过官方机器人生成[@BotFather](https://t.me/BotFather)发送`/newbot`命令按照提示操作  
    group_username为群组用户么必须带有@  
    ⚠️注意:群组必须为公开群组  
    group_url为群组url请将链接填写完整

  - V2board项
    v2board_name为机场名称  
    v2board_url为机场官网地址

- 运行

  ⚠️注意:在运行机器人之前请先将机器人加入群组并设置为管理员，并配置好配置文件（所有配置项均要填写完整），否则机器人无法正常工作。  
  修改任何配置后需要重启机器人才能生效。

  - 开启机器人

    ```bash
    systemctl start cbot_for_v2board.service
    ```

  - 关闭机器人

    ```bash
    systemctl stop cbot_for_v2board.service
    ```

  - 重启机器人

    ```bash
    systemctl restart cbot_for_v2board.service
    ```

## 演示群组

[小C-Airport](https://t.me/cao_airport_group)

## 问题反馈&更新公告

[小C-机器人交流群](https://t.me/cao_bot_group)
[小C-机器人更新公告](https://t.me/cao_bot_channel)
