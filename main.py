import json
import pytz
from datetime import datetime, timedelta

from telethon import TelegramClient
from telethon import functions

# Get it from https://my.telegram.org/
API_ID = ''
API_HASH = ''

BOYS_ID = 1231044699

FEED_TOAD_PERIOD = timedelta(hours=12, minutes=2)
DEALER_JOB_PERIOD = timedelta(hours=8, minutes=5)
TOAD_OF_THE_DAY_PERIOD = timedelta(days=1)

scheduled_messages_count = 0

MESSAGES_LIMIT = 100

client = TelegramClient('session_name', API_ID, API_HASH)

def localize(t):
    if t.tzinfo is None:
        return pytz.UTC.localize(t)
    return t

async def prepare_message(scheduled_messages, message, delay=timedelta(hours=1), time=None):
    sch_msgs = list(filter(lambda msg: msg.message == message, scheduled_messages))
    next_time = datetime.now()
    if len(sch_msgs) > 0:
        next_time = sch_msgs[-1].date + delay
    if time is None:
        time = datetime.now()
    time = localize(time)
    next_time = localize(next_time)
    if time >= next_time:
        return [{'msg': message, 'time': time}]
    return []


async def do_the_job(entity, scheduled_messages):
    messages = []
    # Job (dealer)
    # time = datetime.today() + timedelta(minutes=2)
    job_messages = await prepare_message(scheduled_messages, 'работа крупье', DEALER_JOB_PERIOD)
    if len(job_messages) > 0:
        job_end_time = job_messages[0].get('time') + timedelta(hours=2, minutes=1)
        job_messages.append(messages.append({'msg': 'завершить работу', 'time': job_end_time}))
    messages.extend(job_messages)
    return messages


async def feed_the_toad(entity, scheduled_messages):
    messages = []
    # Feed the toad
    # time = datetime.today() + timedelta(minutes=2)
    messages.extend(await prepare_message(scheduled_messages, 'покормить жабу', FEED_TOAD_PERIOD))
    return messages


async def send_messages(messages, scheduled_messages_count):
    messages = list(filter(lambda o: o is not None, messages))
    sorted_messages = sorted(messages, key=lambda msg_time: msg_time['time'])
    max_msgs = MESSAGES_LIMIT - scheduled_messages_count
    messages_to_send = sorted_messages[0:max_msgs]
    for message in messages_to_send:
        await client.send_message(entity=entity, message=message['msg'], schedule=message['time'] - timedelta(hours=3))


async def main():
    await client.connect()
    entity = await client.get_entity(BOYS_ID)
    res = await client(functions.messages.GetScheduledHistoryRequest(
        peer=entity,
        hash=0
    ))
    scheduled_messages = res.messages
    if scheduled_messages is None:
        scheduled_messages = list()
    scheduled_messages = sorted(scheduled_messages, key=lambda msg: msg.date)
    messages = await feed_the_toad(entity, scheduled_messages)
    messages.extend(await do_the_job(entity, scheduled_messages))
    await send_messages(messages, len(scheduled_messages))


client.loop.run_until_complete(main())