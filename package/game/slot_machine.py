#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import time, uuid, pytz, os, sys, configparser
from datetime import datetime, timezone
from package.job import message_auto_del
from package.database import V2_DB
from telegram.ext import ContextTypes
from telegram import (
    Update, 
    error,
    InlineKeyboardButton,
    InlineKeyboardMarkup
)


DATA_SLOT_MACHINE = {
    "1" : "®️|®️|®️","2" : "🍇|®️|®️","3" : "🍋|®️|®️","4" : "7️⃣|®️|®️",
    "5" : "®️|🍇|®️","6" : "🍇|🍇|®️","7" : "🍋|🍇|®️","8" : "7️⃣|🍇|®️",
    "9" : "®️|🍋|®️","10" : "🍇|🍋|®️","11" : "🍋|🍋|®️","12" : "7️⃣|🍋|®️",
    "13" : "®️|7️⃣|®️","14" : "🍇|7️⃣|®️","15" : "🍋|7️⃣|®️","16" : "7️⃣|7️⃣|®️",
    "17" : "®️|®️|🍇","18" : "🍇|®️|🍇","19" : "🍋|®️|🍇","20" : "7️⃣|®️|🍇",
    "21" : "®️|🍇|🍇","22" : "🍇|🍇|🍇","23" : "🍋|🍇|🍇","24" : "7️⃣|🍇|🍇",
    "25" : "®️|🍋|🍇","26" : "🍇|🍋|🍇","27" : "🍋|🍋|🍇","28" : "7️⃣|🍋|🍇",
    "29" : "®️|7️⃣|🍇","30" : "🍇|7️⃣|🍇","31" : "🍋|7️⃣|🍇","32" : "7️⃣|7️⃣|🍇",
    "33" : "®️|®️|🍋","34" : "🍇|®️|🍋","35" : "🍋|®️|🍋","36" : "7️⃣|®️|🍋",
    "37" : "®️|🍇|🍋","38" : "🍇|🍇|🍋","39" : "🍋|🍇|🍋","40" : "7️⃣|🍇|🍋",
    "41" : "®️|🍋|🍋","42" : "🍇|🍋|🍋","43" : "🍋|🍋|🍋","44" : "7️⃣|🍋|🍋",
    "45" : "®️|7️⃣|🍋","46" : "🍇|7️⃣|🍋","47" : "🍋|7️⃣|🍋","48" : "7️⃣|7️⃣|🍋",
    "49" : "®️|®️|7️⃣","50" : "🍇|®️|7️⃣","51" : "🍋|®️|7️⃣","52" : "7️⃣|®️|7️⃣",
    "53" : "®️|🍇|7️⃣","54" : "🍇|🍇|7️⃣","55" : "🍋|🍇|7️⃣","56" : "7️⃣|🍇|7️⃣",
    "57" : "®️|🍋|7️⃣","58" : "🍇|🍋|7️⃣","59" : "🍋|🍋|7️⃣","60" : "7️⃣|🍋|7️⃣",
    "61" : "®️|7️⃣|7️⃣","62" : "🍇|7️⃣|7️⃣","63" : "🍋|7️⃣|7️⃣","64" : "7️⃣|7️⃣|7️⃣"
}
RGLQ2 = [
    2,3,4,5,9,13,17,33,49,16,32,48,52,56,60,61,62,63,
    11,27,35,39,41,42,44,47,59,6,18,21,23,24,26,30,38,54
]
RGLQ3 = [1,22,43,64]
R2 = [2,3,4,5,9,13,17,33,49]
G2 = [6,18,21,23,24,26,30,38,54]
L2 = [11,27,35,39,41,42,44,47,59]
Q2 = [16,32,48,52,56,60,61,62,63]
R1 = [7,8,10,12,14,15,19,20,25,29,34,36,37,45,50,51,53,57]
G1 = [7,8,10,14,19,20,25,28,29,31,34,37,40,46,50,53,55,58]
L1 = [7,10,12,15,19,25,28,31,34,36,37,40,45,46,51,55,57,58]
Q1 = [8,12,14,15,20,28,29,31,36,40,45,46,50,51,53,55,57,58]

MAIN_FILE_DIR = os.path.dirname(os.path.abspath(sys.modules['__main__'].__file__))
CONF = configparser.ConfigParser()
CONF.read(MAIN_FILE_DIR + '/conf/config.conf')
NAME = CONF.get('V2board','name')
AIRPORT_URL = CONF.get('V2board','url')
GROUP_URL = CONF.get('Telegram','group_url')
GROUP_USERNAME = CONF.get('Telegram','group_username')

#老虎机整体循环秒数
SLOT_MACHINE_TIME = 600
#开奖前返时间
SLOT_MACHINE_END_TIME = 60


async def bet_start(context: ContextTypes.DEFAULT_TYPE):
    '''投注开始'''
    date = (time.strftime('%Y%m%d%H%M', time.gmtime()))
    keyboard = [
            [
                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                InlineKeyboardButton("🔄开奖时间",callback_data='BET_UP:'),
            ], 
            [
                InlineKeyboardButton("📝玩法说明文档",url='https://telegra.ph/CAO-SLOT-MACHINE-03-31'),
            ], 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    bot_return = await context.bot.send_message(chat_id=GROUP_USERNAME, text=f'🎰投注赚流量\n第<code>{date}</code>期开始了🎉\n\n点击下方按钮投注', reply_markup=reply_markup, parse_mode='HTML')

    context.bot_data[date] = {}
    context.bot_data['bet_message'] = f'🎰投注赚流量\n第<code>{date}</code>期开始了🎉\n\n'
    context.bot_data['bet_message_id'] = bot_return.message_id
    context.bot_data['bet_period'] = date

    #添加开奖任务
    context.job_queue.run_once(bet_end, SLOT_MACHINE_TIME-SLOT_MACHINE_END_TIME, name='bet_end')


async def bet_end(context: ContextTypes.DEFAULT_TYPE):
    '''开奖'''
    await context.bot.delete_message(chat_id=GROUP_USERNAME, message_id=context.bot_data['bet_message_id'])

    #发送老虎机获取开奖结果
    bot_return = await context.bot.send_dice(chat_id=GROUP_USERNAME,emoji='🎰')
    lottery_result = (DATA_SLOT_MACHINE[str(bot_return.dice.value)])
    context.job_queue.run_once(message_auto_del, SLOT_MACHINE_END_TIME, data=bot_return.chat_id, name=str(bot_return.message_id))
    
    #开奖结果头部信息
    date = context.bot_data['bet_period']
    first_text = f'第<code>{date}</code>期：开奖结果{lottery_result}\n\n'

    #初始化群组消息
    group_text = ''

    #判断开奖结果
    bet_end = []
    if bot_return.dice.value in RGLQ3:
        bet_end.append('💣')
        if bot_return.dice.value == 1:
            bet_end.append('®️®️®️')
        elif bot_return.dice.value == 22:
            bet_end.append('🍇🍇🍇')
        elif bot_return.dice.value == 43:
            bet_end.append('🍋🍋🍋')
        elif bot_return.dice.value == 64:
            bet_end.append('7️⃣7️⃣7️⃣')
    elif bot_return.dice.value in RGLQ2:
        if bot_return.dice.value in R2:
            bet_end.append('®️®️')
        elif bot_return.dice.value in G2:
            bet_end.append('🍇🍇')
        elif bot_return.dice.value in L2:
            bet_end.append('🍋🍋')
        elif bot_return.dice.value in Q2:
            bet_end.append('7️⃣7️⃣')
    else:
        if bot_return.dice.value in R1:
            bet_end.append('®️')
        if bot_return.dice.value in G1:
            bet_end.append('🍇')
        if bot_return.dice.value in L1:
            bet_end.append('🍋')
        if bot_return.dice.value in Q1:
            bet_end.append('7️⃣')

    #循环开奖结果
    for temp_bet in bet_end:
        #循环用户投注信息
        for temp_data in context.bot_data[date]:
            #单个用户信息
            user_id = context.bot_data[date][temp_data][0]
            user_first_name = context.bot_data[date][temp_data][1]
            user_bet = context.bot_data[date][temp_data][2]
            user_bet_flow = int(context.bot_data[date][temp_data][3])
            
            if user_bet == temp_bet:
                #判断赔率
                if temp_bet == '💣':
                    user_bet_flow *= 15
                elif temp_bet == '®️®️®️' or temp_bet == '🍇🍇🍇' or temp_bet == '🍋🍋🍋' or temp_bet == '7️⃣7️⃣7️⃣':
                    user_bet_flow *= 50
                elif temp_bet == '®️®️' or temp_bet == '🍇🍇' or temp_bet == '🍋🍋' or temp_bet == '7️⃣7️⃣':
                    user_bet_flow *= 6
                elif temp_bet == '®️' or temp_bet == '🍇' or temp_bet == '🍋' or temp_bet == '7️⃣':
                    user_bet_flow *= 2

                end_text = f'投注项:{user_bet}\n恭喜中奖🎉获得{user_bet_flow}GB流量'
            
                group_text += f'{user_first_name}投注{user_bet}中奖获得{user_bet_flow}GB流量\n'

                #发送奖励信息
                await context.bot.send_message(chat_id=int(user_id), text=first_text+end_text, parse_mode='HTML')

                #查询用户信息
                sql = "select * from v2_user where telegram_id=%s"
                val = (int(user_id), )
                myresult = V2_DB.select_one(sql, val)
                #更新用户数据
                u = myresult.get('u')-(int(user_bet_flow)*1073741824)
                d = myresult.get('d')-(int(user_bet_flow)*1073741824)
                transfer_enable = myresult.get('transfer_enable')+(int(user_bet_flow)*1073741824)
                if u >= 0:
                    sql = "update v2_user set u=%s where telegram_id=%s"
                    val = (u, int(user_id))
                    V2_DB.update_one(sql, val)
                elif d >= 0:
                    sql = "update v2_user set d=%s where telegram_id=%s"
                    val = (d, int(user_id))
                    V2_DB.update_one(sql, val)
                else:
                    sql = "update v2_user set transfer_enable=%s where telegram_id=%s"
                    val = (transfer_enable, int(user_id))
                    V2_DB.update_one(sql, val)
                #统计获奖流量
                if 'award_flow' in context.bot_data:
                    context.bot_data['award_flow'] += int(user_bet_flow)
                else:
                    context.bot_data['award_flow'] = 0
                    context.bot_data['award_flow'] += int(user_bet_flow)

    if group_text:
        pass
    else:
        group_text += '本期无人中奖👻'

    #发送群组奖励信息
    message_return = await context.bot.send_message(chat_id=GROUP_USERNAME,text=first_text+group_text, parse_mode='HTML')
    if group_text == '本期无人中奖👻':
        context.job_queue.run_once(message_auto_del, SLOT_MACHINE_END_TIME, data=message_return.chat_id, name=str(message_return.message_id))

    bet_result_data = f'第<code>{date}</code>期：开奖结果{lottery_result}\n'
    context.job_queue.run_once(bet_result, SLOT_MACHINE_END_TIME, name='bet_result', data=bet_result_data)

    del context.bot_data['bet_message_id']
    del context.bot_data['bet_message']
    del context.bot_data['bet_period']
    del context.bot_data[date]


async def bet_result(context: ContextTypes.DEFAULT_TYPE):
    '''统计开奖记录'''
    if 'bet_result' in context.bot_data:
        context.bot_data['bet_result'] += context.job.data
    else:
        context.bot_data['bet_result'] = ''
        context.bot_data['bet_result'] += context.job.data


async def bet_flow(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注流量'''
    date = update.callback_query.data.split(':')[1].split(',')[0]
    bet_content = update.callback_query.data.split(':')[1].split(',')[1]
    
    #查询用户信息
    sql = "select * from v2_user where telegram_id=%s"
    val = (update.callback_query.from_user.id, )
    myresult = V2_DB.select_one(sql, val)
    if not myresult:
        await update.callback_query.answer(text='投注失败')
        await update.callback_query.edit_message_text('投注失败❌\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
        return
    
    #查询可用流量
    u = myresult.get('u')
    d = myresult.get('d')
    transfer_enable = myresult.get('transfer_enable')
    transfer = round((transfer_enable-u-d)/1073741824, 2)
    #生成按钮
    keyboard = [
            [
                InlineKeyboardButton("1GB",callback_data=f'BET_FLOW:{date},1,'),
                InlineKeyboardButton("2GB",callback_data=f'BET_FLOW:{date},2,'),
                InlineKeyboardButton("5GB",callback_data=f'BET_FLOW:{date},5,'),
            ], 
            [
                InlineKeyboardButton("10GB",callback_data=f'BET_FLOW:{date},10,'),
                InlineKeyboardButton("20GB",callback_data=f'BET_FLOW:{date},20,'),
                InlineKeyboardButton("50GB",callback_data=f'BET_FLOW:{date},50,'),
            ], 
            [
                InlineKeyboardButton("100GB",callback_data=f'BET_FLOW:{date},100,'),
            ], 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    #更改页面消息
    try:
        await update.callback_query.answer(text='已切换显示')
        await update.callback_query.edit_message_text(text=f'您当前剩余可用流量{transfer}GB\n\n请选择您的投注流量:',reply_markup=reply_markup)
    except error.BadRequest:
        pass
    context.user_data['bet_content'] = bet_content
        

async def bet_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''放弃投注'''
    if 'bet_content' in context.user_data:
        del context.user_data['bet_content']
    if 'bet_flow' in context.user_data:
        del context.user_data['bet_flow']
    try:
        keyboard = [
                [
                    InlineKeyboardButton("🔙返回群组",url=GROUP_URL),
                ], 
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.answer(text='投注已放弃')
        await update.callback_query.edit_message_text('投注已放弃❌\n若要重新投注请返回群组重新投注', reply_markup=reply_markup)
    except error.BadRequest:
        pass


async def bet_ok_no(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注确认'''
    try:
        #按钮数据分离
        date = update.callback_query.data.split(':')[1].split(',')[0]
        bet_flow = update.callback_query.data.split(':')[1].split(',')[1]
        context.user_data['bet_flow'] = bet_flow
        bet_content = context.user_data['bet_content']
        #生成按钮
        keyboard = [
                [
                    InlineKeyboardButton("✅确认",callback_data='BET_OK:'),
                    InlineKeyboardButton("❌放弃",callback_data='BET_NO:'),
                ], 
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        #编辑消息
        await update.callback_query.answer(text='已切换显示')
        await update.callback_query.edit_message_text(text=f'确认您的投注内容❗️\n\n第<code>{date}</code>期\n投注{bet_content}流量{bet_flow}GB', reply_markup=reply_markup, parse_mode='HTML')
    except KeyError:
        await update.callback_query.answer(text='已切换显示')
        await update.callback_query.edit_message_text(text=f'投注失败❌\n本期已开奖或投注期数错误\n请返回群组重新开始投注')


async def bet_ok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''投注成功'''
    try:
        #分离数据
        date = context.bot_data['bet_period']
        bet_content = context.user_data['bet_content']
        bet_flow = context.user_data['bet_flow']
        del context.user_data['bet_content']
        del context.user_data['bet_flow']
        #查询用户数据
        sql = "select * from v2_user where telegram_id=%s"
        val = (update.callback_query.from_user.id, )
        myresult = V2_DB.select_one(sql, val)
        if myresult:
            #查询开奖剩余秒数
            current_jobs = context.job_queue.get_jobs_by_name('bet_end')
            limit_time = (current_jobs[0].job.next_run_time - datetime.now(timezone.utc)).seconds
            if limit_time > 10:
                #计算流量
                u = myresult.get('u')
                d = myresult.get('d')
                transfer_enable = myresult.get('transfer_enable')
                used_transfer = int((u+d)/1073741824)
                transfer = int((transfer_enable)/1073741824)
                if used_transfer + int(bet_flow) <= transfer:
                    #添加bot数据
                    context.bot_data[date][str(uuid.uuid4())] = [update.callback_query.from_user.id, update.callback_query.from_user.first_name, bet_content, bet_flow]
                    #删除群组消息
                    await context.bot.delete_message(chat_id=GROUP_USERNAME, message_id=context.bot_data['bet_message_id'])
                    #读取旧数据
                    old_message_list = context.bot_data['bet_message'].split('\n\n')
                    try:
                        old_message = old_message_list[1]
                    except:
                        old_message = ''
                    #生成信息
                    first_text = f'🎰投注赚流量\n第<code>{date}</code>期\n剩余开奖时间{limit_time}秒\n\n'
                    new_text = f'{update.callback_query.from_user.first_name}投注{bet_content}流量{bet_flow}GB\n'
                    context.bot_data['bet_message'] = first_text+old_message+new_text
                    #发送成功消息
                    keyboard = [
                            [
                                InlineKeyboardButton("🔙返回群组",url=GROUP_URL),
                            ], 
                        ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    await update.callback_query.answer(text='投注成功')
                    await update.callback_query.edit_message_text(text=f'投注成功🎉\n\n第<code>{date}</code>期\n投注{bet_content}流量{bet_flow}GB\n\n如有中奖会通知您\n您可返回群组等待开奖结果', parse_mode='HTML',reply_markup=reply_markup)
                    #发送新群组消息
                    keyboard = [
                            [
                                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                                InlineKeyboardButton("🔄开奖时间",callback_data='BET_UP:'),
                            ], 
                            [
                                InlineKeyboardButton("📝玩法说明文档",url='https://telegra.ph/CAO-SLOT-MACHINE-03-31'),
                            ], 
                        ]
                    reply_markup = InlineKeyboardMarkup(keyboard)
                    bot_return = await context.bot.send_message(chat_id=GROUP_USERNAME, text=context.bot_data['bet_message'], reply_markup=reply_markup, parse_mode='HTML')
                    context.bot_data['bet_message_id'] = bot_return.message_id
                    #更新用户数据
                    u = (int(bet_flow)*1073741824)+u
                    sql = "update v2_user set u=%s where telegram_id=%s"
                    val = (u, update.callback_query.from_user.id)
                    V2_DB.update_one(sql, val)
                    #初始统计下注流量
                    if 'bet_all_flow' in context.bot_data:
                        context.bot_data['bet_all_flow'] += int(bet_flow)
                    else:
                        context.bot_data['bet_all_flow'] = 0
                        context.bot_data['bet_all_flow'] += int(bet_flow)
                else:
                    await update.callback_query.answer(text='投注失败')
                    await update.callback_query.edit_message_text(text=f'投注失败❌\n可用流量不足\n禁止投注\n使用 /me 命令可查询可用流量')
            else:
                await update.callback_query.answer(text='投注失败')
                await update.callback_query.edit_message_text(text=f'投注失败❌\n距离开奖时间小于10秒\n禁止投注')
        else:
            await update.callback_query.answer(text='投注失败')
            await update.callback_query.edit_message_text('投注失败❌\n您还没有绑定账号\n请使用 /bind 命令绑定账号后使用')
    except KeyError:
        await update.callback_query.answer(text='投注失败')
        keyboard = [
                [
                    InlineKeyboardButton("🔙返回群组",url=GROUP_URL),
                ], 
            ]
        reply_markup = InlineKeyboardMarkup(keyboard)
        await update.callback_query.edit_message_text(text=f'投注失败❌\n本期已开奖或投注期数错误\n请返回群组重新开始投注',reply_markup=reply_markup)
    except error.BadRequest:
        pass


async def bet_up(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''更新开奖时间'''
    current_jobs = context.job_queue.get_jobs_by_name('bet_end')
    limit_time = (current_jobs[0].job.next_run_time - datetime.now(timezone.utc)).seconds
    date = context.bot_data['bet_period']

    #读取旧数据
    old_message_list = context.bot_data['bet_message'].split('\n\n')
    try:
        old_message = old_message_list[1]
    except:
        old_message = ''

    #生成信息
    first_text = f'🎰投注赚流量\n第<code>{date}</code>期\n剩余开奖时间{limit_time}秒\n\n'
    context.bot_data['bet_message'] = first_text+old_message
    
    #更改群组消息
    keyboard = [
            [
                InlineKeyboardButton("📥我要投注",url=f'{context.bot.link}?start={date}'),
                InlineKeyboardButton("🔄开奖时间",callback_data='BET_UP:'),
            ], 
            [
                InlineKeyboardButton("📝玩法说明文档",url='https://telegra.ph/CAO-SLOT-MACHINE-03-31'),
            ], 
        ]
    reply_markup = InlineKeyboardMarkup(keyboard)
    await update.callback_query.answer(text='更新开奖时间成功')
    await update.callback_query.edit_message_text(text=context.bot_data['bet_message'], reply_markup=reply_markup, parse_mode='HTML')


async def lottery_record(update: Update, context: ContextTypes.DEFAULT_TYPE):
    '''开奖记录查询'''
    bot_return = await update.message.reply_text(text=context.bot_data['bet_result'], parse_mode='HTML')
    if update.message.chat.type == 'supergroup':
        context.job_queue.run_once(message_auto_del, 30, data=update.message.chat_id, name=str(update.message.message_id))
        context.job_queue.run_once(message_auto_del, 30, data=bot_return.chat_id, name=str(bot_return.message_id))
