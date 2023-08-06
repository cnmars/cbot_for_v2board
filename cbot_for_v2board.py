#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import logging, configparser, os
from datetime import datetime, timedelta
from package import check_in, command
from package.game import slot_machine, lottery_record
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters,
)


MODULE_REAL_DIR = os.path.dirname(os.path.realpath(__file__))
FILENAME = os.path.splitext(os.path.basename(__file__))[0]
CONF = configparser.ConfigParser()
CONF.read(MODULE_REAL_DIR + '/conf/config.conf')
TOKEN = CONF.get('Telegram', FILENAME)
logging.basicConfig(
    #filename=MODULE_REAL_DIR + '/log/' + FILENAME + '.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', 
    level=logging.INFO
)
logging.getLogger("httpx").setLevel(logging.WARNING)
logging.getLogger('apscheduler').setLevel(logging.WARNING)
logger = logging.getLogger(__name__)


def calculate_remaining_seconds():
    '''计算距离最近的整10分钟剩余秒数'''
    current_time = datetime.now()
    # 取整10分钟
    nearest_minute = (current_time.minute // 10) * 10 + 10
    nearest_minute %= 60
    # 取整10分钟的时间
    nearest_10_minutes = current_time.replace(minute=nearest_minute, second=0, microsecond=0)
    if nearest_10_minutes < current_time:
        nearest_10_minutes += timedelta(hours=1)
    # 计算时间差
    time_difference = nearest_10_minutes - current_time
    # 返回剩余秒数
    return time_difference.seconds + 10


def main():
    #机器人令牌
    application = Application.builder().token(TOKEN).build()

    #触发下注开始任务
    application.job_queue.run_repeating(
        callback=slot_machine.bet_start, 
        interval=600, 
        first=calculate_remaining_seconds(), 
        name='bet_start'
    )

    #命令
    application.add_handler(CommandHandler('help', command.start))
    application.add_handler(CommandHandler('start', command.start))
    application.add_handler(CommandHandler('bind', command.bind))
    application.add_handler(CommandHandler('login', command.login))
    application.add_handler(CommandHandler('unbind', command.unbind))
    application.add_handler(CommandHandler('logout', command.unbind))
    application.add_handler(CommandHandler('me', command.me))
    application.add_handler(CommandHandler('day', check_in.day))
    application.add_handler(CommandHandler('lottery_record', lottery_record.lottery_record))
    application.add_handler(CommandHandler('change_password', command.change_password))
    
    #下注按钮
    application.add_handler(CallbackQueryHandler(slot_machine.bet_up,pattern='^BET_UP:'))
    application.add_handler(CallbackQueryHandler(slot_machine.bet_ok,pattern='^BET_OK:'))
    application.add_handler(CallbackQueryHandler(slot_machine.bet_no,pattern='^BET_NO:'))
    application.add_handler(CallbackQueryHandler(slot_machine.bet_ok_no,pattern='^BET_FLOW:'))
    application.add_handler(CallbackQueryHandler(slot_machine.bet_flow,pattern='^BET_CONTENT:'))

    #签到按钮
    application.add_handler(CallbackQueryHandler(check_in.check_in_keyboard,pattern='^DAY:'))

    #开奖记录按钮
    application.add_handler(CallbackQueryHandler(lottery_record.lottery_record_page,pattern='^LOTTERY_RECORD:'))

    #过滤转发签到表情,防止刷签到
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.DICE, check_in.forwarded_dice))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.DARTS, check_in.forwarded_dice))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.BOWLING, check_in.forwarded_dice))
    application.add_handler(MessageHandler(filters.FORWARDED & filters.Dice.SLOT_MACHINE, check_in.forwarded_dice))
    
    #过滤骰子普通签到
    application.add_handler(MessageHandler(filters.Dice.DICE, check_in.dice6))
    application.add_handler(MessageHandler(filters.Dice.DARTS, check_in.dice6))
    application.add_handler(MessageHandler(filters.Dice.BOWLING, check_in.dice6))

    #过滤老虎机疯狂签到
    application.add_handler(MessageHandler(filters.Dice.SLOT_MACHINE, check_in.dice_slot_machine))
    
    #开启机器人
    application.run_polling()


if __name__ == '__main__':
    main()




