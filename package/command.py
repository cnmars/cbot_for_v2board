#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import time, bcrypt, os, sys, configparser
from package.job import message_auto_del
from package.database import V2_DB
from telegram.ext import ContextTypes
from telegram import Update, error, InlineKeyboardButton, InlineKeyboardMarkup


MAIN_FILE_DIR = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
CONF = configparser.ConfigParser()
CONF.read(MAIN_FILE_DIR + '/conf/config.conf')
AIRPORT_URL = CONF.get('V2board','url')
GROUP_URL = CONF.get('Telegram','group_url')
NAME = CONF.get('V2board','name')


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''start命令'''
    if not update.message:
        return

    if update.message.chat.type == 'supergroup':
        try:
            await update.message.delete()
        except error.BadRequest:
            pass
        return
    
    if not context.args:
        keyboard = [
            [
                InlineKeyboardButton("🌍官方网站", url=AIRPORT_URL),
                InlineKeyboardButton("👥官方群组", url=GROUP_URL),
            ],
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(
            text=f'Hi\n欢迎使用{NAME}机场bot\n\n'\
                f'如果您没有注册过{NAME}请点击下方按钮进入官方网站注册\n\n'\
                '如果您已注册,请使用 /bind 命令绑定账号后使用此Bot',
            reply_markup=reply_markup,
        )
        return
        
    if len(context.args) == 1:
        keyboard = [
            [
                InlineKeyboardButton("®️®️®️",callback_data=f'BET_CONTENT:{context.args[0]},®️®️®️,'),
                InlineKeyboardButton("🍇🍇🍇",callback_data=f'BET_CONTENT:{context.args[0]},🍇🍇🍇,'),
                InlineKeyboardButton("🍋🍋🍋",callback_data=f'BET_CONTENT:{context.args[0]},🍋🍋🍋,'),
                InlineKeyboardButton("7️⃣7️⃣7️⃣",callback_data=f'BET_CONTENT:{context.args[0]},7️⃣7️⃣7️⃣,'),
            ], 
            [
                InlineKeyboardButton("®️®️",callback_data=f'BET_CONTENT:{context.args[0]},®️®️,'),
                InlineKeyboardButton("🍇🍇",callback_data=f'BET_CONTENT:{context.args[0]},🍇🍇,'),
                InlineKeyboardButton("🍋🍋",callback_data=f'BET_CONTENT:{context.args[0]},🍋🍋,'),
                InlineKeyboardButton("7️⃣7️⃣",callback_data=f'BET_CONTENT:{context.args[0]},7️⃣7️⃣,'),
            ], 
            [
                InlineKeyboardButton("®️",callback_data=f'BET_CONTENT:{context.args[0]},®️,'),
                InlineKeyboardButton("🍇",callback_data=f'BET_CONTENT:{context.args[0]},🍇,'),
                InlineKeyboardButton("🍋",callback_data=f'BET_CONTENT:{context.args[0]},🍋,'),
                InlineKeyboardButton("7️⃣",callback_data=f'BET_CONTENT:{context.args[0]},7️⃣,'),
            ], 
            [
                InlineKeyboardButton("特殊奖:炸弹💣",callback_data=f'BET_CONTENT:{context.args[0]},💣,'),
            ], 
        ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.message.reply_text(text='请选择您的投注项:',reply_markup=reply_markup)
                

async def bind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''绑定账号'''
    if  not update.message:
        return

    if update.message.chat.type == 'supergroup':
        bot_return = await update.message.reply_text(f'为了避免个人信息泄漏\n请私聊机器人进行绑定\n{context.bot.link}')
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if myresult:
        email = myresult.get('email')
        await update.message.reply_text(f'当前已经绑定{email}邮箱\n若要绑定其他账号请先发送 /unbind 解除绑定')
        return

    if not context.args:
        await update.message.reply_text(
            text=f'如需将{NAME}绑定Telegram请使用此命令+订阅地址进行绑定\n\n'\
                f'例如:\n/bind {AIRPORT_URL}/api/v1/client/subscribe?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n'\
                f'订阅地址请在{NAME}官网 {AIRPORT_URL} 仪表盘 -> 一键订阅 -> 复制订阅地址 获取',
            )
        return    
            
    if len(context.args) != 1:
        await update.message.reply_text(
            text='❌命令格式错误\n'\
                f'如需将{NAME}绑定Telegram请使用此命令+订阅地址进行绑定\n\n'\
                f'例如:\n/bind {AIRPORT_URL}/api/v1/client/subscribe?token=xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx\n\n'\
                f'订阅地址请在{NAME}官网 {AIRPORT_URL} 仪表盘 -> 一键订阅 -> 复制订阅地址 获取',
            )
        return 
        
    #获取用户token
    l_link = (context.args[0]).split('token=')
    if '&' in l_link[1]:
        token = l_link[1].split('&')[0]
    else:
        token = l_link[1]
    #查询用户token
    sql = "select * from v2_user where token like %s"
    myresult = V2_DB.select_one(sql, (token, ))
    if myresult:
        sql = "update v2_user set telegram_id=%s where token=%s"
        val = (update.message.from_user.id, token, )
        V2_DB.update_one(sql, val)
        await update.message.reply_text('✅绑定成功\n使用命令 /me 查看我的信息')
    else:
        await update.message.reply_text('未查询到此订阅信息,请核对后再试...')


async def unbind(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''解除绑定'''
    if  not update.message:
        return
    
    if update.message.chat.type == 'supergroup':
        bot_return = await update.message.reply_text(f'为了避免个人信息泄漏\n请私聊机器人进行绑定\n{context.bot.link}')
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    sql = "update v2_user set telegram_id=NULL where telegram_id=%s"
    val = (update.message.from_user.id, )
    db_status = V2_DB.update_one(sql, val)
    if db_status:
        await update.message.reply_text('✅退出登录/解除绑定成功')
    else:
        await update.message.reply_text(f'您没有绑定过{NAME}\n无需解绑')


async def me(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''查询个人信息'''
    if not update.message:
        return

    if update.message.chat.type == 'supergroup':
        bot_return = await update.message.reply_text(f'为了避免个人信息泄漏\n请私聊机器人进行查询\n{context.bot.link}')
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        await update.message.reply_text('您还没有绑定账号\n请先发送 /bind 进行绑定后再试...')
        return
    
    #账户余额
    balance = round((myresult.get('balance') / 100), 2) if myresult.get('balance') else 0.0
    #邮箱账号
    email = myresult.get('email')
    #订阅到期
    expired_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(myresult.get('expired_at')))
    #流量更新日期
    updated_at = time.strftime("%Y-%m-%d %H:%M:%S", time.localtime(myresult.get('updated_at')))
    #获取流量
    u = myresult.get('u')
    d = myresult.get('d')
    transfer_enable = myresult.get('transfer_enable')
    #已用流量
    used_transfer = round(((u+d)/1073741824), 2)
    #可用流量
    transfer = round(((transfer_enable-u-d)/1073741824), 2)
    #订阅名称
    plan_id = myresult.get('plan_id')
    sql = "select * from v2_plan where id=%s"
    val = (plan_id, )
    myresult = V2_DB.select_one(sql, val)
    plan_name = myresult.get('name')
    #发送信息
    await update.message.reply_text(
        text='👤用户信息\n'\
            f' ┝TGID: '+str(update.message.from_user.id)+'\n'\
            f' ┝账户邮箱: '+str(email)+'\n'\
            f' ┝账户余额: '+str(balance)+'\n'\
            f' ┝我的套餐: '+str(plan_name)+'\n'\
            f' ┝已用流量: '+str(used_transfer)+'GB\n'\
            f' ┝可用流量: '+str(transfer)+'GB\n'\
            f' ┝套餐到期: '+str(expired_at)+'\n'\
            f' ┕流量更新: '+str(updated_at),
        )


async def change_password(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''更改密码'''
    if not update.message:
        return

    if update.message.chat.type == 'supergroup':
        bot_return = await update.message.reply_text(f'为了避免个人信息泄漏\n请私聊机器人进行更改密码\n{context.bot.link}')
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    if not context.args:
        await update.message.reply_text(
        text='若要更改密码请使用此命令+新密码进行更改\n\n'\
            '例如:将密码更改为12345678\n'\
            '/change_password 12345678'
        )
        return
            
    if len(context.args[0]) != 1:
        await update.message.reply_text(
        text='❌命令格式错误\n\n'\
            '若要更改密码请使用此命令+新密码进行更改\n\n'\
            '例如:将密码更改为12345678\n'\
            '/change_password 12345678'
        )
        return
    
    #获取用户输入密码的字节串
    password = str(context.args[0]).encode('utf-8')
    #设置计算成本用于符合v2b面板的生成结果
    salt = bcrypt.gensalt(10)
    #生成hash
    hash = bcrypt.hashpw(password, salt)
    #将哈希值中的$2b替换为$2y用于符合v2b面板的生成结果
    hash = hash.decode('utf-8').replace('$2b$', '$2y$')
    #存储数据库
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if myresult:
        sql = "update v2_user set password=%s where telegram_id=%s"
        val = (hash, update.message.from_user.id, )
        V2_DB.update_one(sql, val)
        await update.message.reply_text(f'✅更改密码成功\n请使用新密码登录官网\n官网地址{AIRPORT_URL}')
    else:
        await update.message.reply_text('❌未查询到此Telegram账号绑定信息,请先使用 /bind 绑定后再试...')
           

async def login(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''登录绑定'''
    if not update.message:
        return

    if update.message.chat.type == 'supergroup':
        bot_return = await update.message.reply_text(f'为了避免个人信息泄漏\n请私聊机器人进行登录\n{context.bot.link}')
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if myresult:
        email = myresult.get('email')
        await update.message.reply_text(f'当前已经绑定{email}邮箱\n若要绑定其他账号请先发送 /unbind 解除绑定')
        return

    if not context.args:
        await update.message.reply_text(
            text='若要登录绑定请使用此命令+邮箱+密码进行登录\n\n'\
                '例如:\n/login 12345678@qq.com 12345678'
        )
        return

    if len(context.args) != 2:
        await update.message.reply_text(
            text='❌命令格式错误\n\n'\
                '若要登录绑定请使用此命令+邮箱+密码进行登录\n\n'\
                '例如:\n/login 12345678@qq.com 12345678'
        )
        return
    
    sql = "select * from v2_user where email = %s"
    val = (context.args[0], )
    myresult = V2_DB.select_one(sql, val)
    if myresult:
        in_passwd = str(context.args[1]).encode('utf-8')
        db_passwd = str(myresult.get('password')).encode('utf-8')
        if bcrypt.checkpw(in_passwd, db_passwd):
            sql = "update v2_user set telegram_id=%s where email=%s"
            val = (update.message.from_user.id, context.args[0], )
            V2_DB.update_one(sql, val)
            await update.message.reply_text('✅登录绑定成功\n使用命令 /me 查看我的信息')
        else:
            await update.message.reply_text(f'⚠️输入的邮箱密码不正确\n请确认后再试...')
    else:
        await update.message.reply_text(f'⚠️未查询到此邮箱注册\n请进入官网注册后再试\n官网地址{AIRPORT_URL}')

