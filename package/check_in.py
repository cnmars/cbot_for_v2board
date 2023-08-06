#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import random
from package.job import message_auto_del, del_limit, find_limit_time
from package.database import V2_DB
from telegram.ext import ContextTypes
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup


async def day(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''每日签到'''
    keyboard = [
        [
            InlineKeyboardButton('普通签到', callback_data='DAY:dice,'),
        ],
        [
            InlineKeyboardButton('疯狂签到', callback_data='DAY:machine,'),
        ]
    ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await update.message.reply_text(
        text='发送「🎲」「🎳」「🎯」三个emoji表情里的任意一个。进行普通签到。可以随机获得0.01-0.06元\n\n'\
        '发送「🎰」老虎机emoji表情。进行疯狂签到。可随机获得0、0.5、1元\n\n'\
        '没人每天可分别进行一次普通签到和疯狂签到。发送emoji表情或点击按钮进行签到。',
        reply_markup=reply_markup
    )
    if update.message.chat.type == 'supergroup':
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


async def dice6(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''普通签到'''    
    dice_job = find_limit_time(context, update.message.from_user.id, 'dice')
    machine_job = find_limit_time(context, update.message.from_user.id, 'machine')
    
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        bot_return = await update.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return

    if dice_job and not machine_job:
        bot_return = await update.message.reply_text('您今天已经进行过普通签到了\n还可以进行一次疯狂签到\n快发送「🎰」试试手气')
    elif dice_job and machine_job:
        bot_return = await update.message.reply_text('您今天已经进行过双重签到了,请明日再试。。。')
    else:
        #查询临时数据
        dice_value = update.message.dice.value
        show_dice_value = int(dice_value)/100
        bot_return = await update.message.reply_text('✅签到成功\n🎉恭喜获得'+str(show_dice_value)+'元')
        #更新用户余额
        sql = 'update v2_user set balance=%s where telegram_id=%s'
        val = (myresult.get('balance')+dice_value, update.message.from_user.id)
        V2_DB.update_one(sql, val)
        #限制每天签到一次
        context.job_queue.run_once(del_limit, 86400, data=update.message.from_user.id, name=str(update.message.from_user.id)+'dice')
    if update.message.chat.type == 'supergroup':
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


async def dice_slot_machine(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''疯狂签到'''
    dice_job = find_limit_time(context, update.message.from_user.id, 'dice')
    machine_job = find_limit_time(context, update.message.from_user.id, 'machine')
    
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.message.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        bot_return = await update.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        return
    
    if not dice_job and machine_job:
        bot_return = await update.message.reply_text('您今天已经进行过疯狂签到了\n还可以进行一次普通签到\n发送「🎲」「🎳」「🎯」其中一个即可,保底可得0.01元')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
    elif dice_job and machine_job:
        bot_return = await update.message.reply_text('您今天已经进行过双重签到了,请明日再试。。。')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
    else:
        dice_value = update.message.dice.value
        if dice_value == 1 or dice_value == 22 or dice_value == 43:
            value = 50
        elif dice_value == 64:
            value = 100
        else:
            value = 0
        if value == 0:
            bot_return = await update.message.reply_text('签到成功\n👻很遗憾今日签到未中奖获得0元')
            if update.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        else:
            show_dice_value = value / 100
            bot_return = await update.message.reply_text('✅签到成功\n🎉恭喜获得'+str(show_dice_value)+'元')
            #更新用户余额
            sql = 'update v2_user set balance=%s where telegram_id=%s'
            val = (myresult.get('balance')+value, update.message.from_user.id)
            V2_DB.update_one(sql, val)
        #限制每天签到一次
        context.job_queue.run_once(del_limit, 86400, data=update.message.from_user.id, name=str(update.message.from_user.id)+'dice')


async def forwarded_dice(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if update.message.dice:
        bot_return = await update.message.reply_text('请不要转发他人签到,重新发送')
        if update.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


async def check_in_keyboard(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''签到按钮'''
    day_type = update.callback_query.data.split(':')[1].split(',')[0]
    if day_type == 'dice':
        emoji = random.choice(['🎲', '🎳', '🎯'])
        dice_return = await update.callback_query.message.reply_dice(emoji=emoji)
        await update.callback_query.message.delete()
        dice_job = find_limit_time(context, update.callback_query.message.from_user.id, 'dice')
        machine_job = find_limit_time(context, update.callback_query.message.from_user.id, 'machine')
        
        sql = "select * from v2_user where telegram_id=%s"
        val = (update.callback_query.message.from_user.id, )
        myresult = V2_DB.select_one(sql, val)
        if not myresult:
            bot_return = await update.callback_query.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
            if update.callback_query.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=update.callback_query.message.chat_id, name=str(update.callback_query.message.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
            return

        if dice_job and not machine_job:
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过普通签到了\n还可以进行一次疯狂签到\n快发送「🎰」试试手气')
        elif dice_job and machine_job:
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过双重签到了,请明日再试。。。')
        else:
            #查询临时数据
            dice_value = dice_return.dice.value
            show_dice_value = int(dice_value)/100
            bot_return = await update.callback_query.message.reply_text('✅签到成功\n🎉恭喜获得'+str(show_dice_value)+'元')
            #更新用户余额
            sql = 'update v2_user set balance=%s where telegram_id=%s'
            val = (myresult.get('balance')+dice_value, update.callback_query.message.from_user.id)
            V2_DB.update_one(sql, val)
            #限制每天签到一次
            context.job_queue.run_once(del_limit, 86400, data=update.callback_query.message.from_user.id, name=str(update.callback_query.message.from_user.id)+'dice')
        if update.callback_query.message.chat.type == 'supergroup':
            context.job_queue.run_once(message_auto_del, 30, data=update.callback_query.message.chat_id, name=str(update.callback_query.message.message_id))
            context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))


    elif day_type == 'machine':
        dice_return = await update.callback_query.message.reply_dice(emoji='🎰')
        await update.callback_query.message.delete()
        dice_job = find_limit_time(context, update.callback_query.message.from_user.id, 'dice')
        machine_job = find_limit_time(context, update.callback_query.message.from_user.id, 'machine')
        
        sql = "select * from v2_user where telegram_id=%s"
        val = (update.callback_query.message.from_user.id, )
        myresult = V2_DB.select_one(sql, val)
        if not myresult:
            bot_return = await update.callback_query.message.reply_text('❌签到失败\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
            if update.callback_query.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=update.callback_query.message.chat_id, name=str(update.callback_query.message.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
            return
        
        if not dice_job and machine_job:
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过疯狂签到了\n还可以进行一次普通签到\n发送「🎲」「🎳」「🎯」其中一个即可,保底可得0.01元')
            if update.callback_query.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=update.callback_query.message.chat_id, name=str(update.callback_query.message.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        elif dice_job and machine_job:
            bot_return = await update.callback_query.message.reply_text('您今天已经进行过双重签到了,请明日再试。。。')
            if update.callback_query.message.chat.type == 'supergroup':
                context.job_queue.run_once(message_auto_del, 30, data=update.callback_query.message.chat_id, name=str(update.callback_query.message.message_id))
                context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
        else:
            dice_value = dice_return.dice.value
            if dice_value == 1 or dice_value == 22 or dice_value == 43:
                value = 50
            elif dice_value == 64:
                value = 100
            else:
                value = 0
            if value == 0:
                bot_return = await update.callback_query.message.reply_text('签到成功\n👻很遗憾今日签到未中奖获得0元')
                if update.callback_query.message.chat.type == 'supergroup':
                    context.job_queue.run_once(message_auto_del, 30, data=update.callback_query.message.chat_id, name=str(update.callback_query.message.message_id))
                    context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
            else:
                show_dice_value = value / 100
                bot_return = await update.callback_query.message.reply_text('✅签到成功\n🎉恭喜获得'+str(show_dice_value)+'元')
                #更新用户余额
                sql = 'update v2_user set balance=%s where telegram_id=%s'
                val = (myresult.get('balance')+value, update.callback_query.message.from_user.id)
                V2_DB.update_one(sql, val)
            #限制每天签到一次
            context.job_queue.run_once(del_limit, 86400, data=update.callback_query.message.from_user.id, name=str(update.callback_query.message.from_user.id)+'dice')


