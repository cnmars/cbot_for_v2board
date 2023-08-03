#!/usr/bin/python
# pylint: disable=C0116,W0613
# -*- coding: utf-8 -*-

import logging
from datetime import datetime, timezone
from telegram import error
from telegram.ext import ContextTypes
logger = logging.getLogger(__name__)


async def message_auto_del(context: ContextTypes.DEFAULT_TYPE):
    '''自动删除消息作业'''
    try:
        await context.bot.delete_message(context.job.data, int(context.job.name))
        current_jobs = context.job_queue.get_jobs_by_name(context.job.name)
        for job in current_jobs:
            job.schedule_removal()
    except (error.BadRequest, error.TimedOut, error.Forbidden, error.RetryAfter) as e:
        logger.error(e)


async def del_limit(context: ContextTypes.DEFAULT_TYPE):
    '''删除限制任务'''
    current_jobs = context.job_queue.get_jobs_by_name(context.job.name)
    for job in current_jobs:
        job.schedule_removal()


async def find_limit_time(context: ContextTypes.DEFAULT_TYPE, user_id: int, limit_type: str):
    '''查询限制任务'''
    current_jobs = context.job_queue.get_jobs_by_name(str(user_id)+limit_type)
    if current_jobs:
        limit_time = (current_jobs[0].job.next_run_time - datetime.now(timezone.utc)).seconds
        return limit_time
    else:
        return 0

