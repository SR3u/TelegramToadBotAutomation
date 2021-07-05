import json
from datetime import datetime, timedelta

from telethon import TelegramClient

# Get it from https://my.telegram.org/
API_ID = ''
API_HASH = ''

BOYS_ID = 1231044699

FEED_TOAD_PERIOD = timedelta(hours=8, minutes=2)
DEALER_JOB_PERIOD = timedelta(hours=8, minutes=5)
TOAD_OF_THE_DAY_PERIOD = timedelta(days=1)

toad_state = None

try:
    with open("toad_state.json", "r") as read_file:
        toad_state = json.load(read_file)
except Exception:
    print('not found')

if toad_state is None:
    toad_state = dict(
        feed=datetime.min,
        job=datetime.min,
    )
else:
    toad_state['feed'] = datetime.fromtimestamp(toad_state['feed'])
    toad_state['job'] = datetime.fromtimestamp(toad_state['job'])

MESSAGES_LIMIT = 100

client = TelegramClient('session_name', API_ID, API_HASH)


def prepare_message(time, message, key, state, delay=timedelta(hours=1)):
    messages = []
    next_time = toad_state[key] + delay
    if time >= next_time:
        messages.append({'msg': message, 'time': time})
        toad_state[key] = time + delay
    return messages


def do_the_job():
    messages = []
    # Job (dealer)
    time = datetime.today() + timedelta(minutes=2)
    job_messages = prepare_message(time, 'работа крупье', 'job', toad_state, DEALER_JOB_PERIOD)
    if len(job_messages) > 0:
        job_messages.append({'msg': 'завершить работу', 'time': time + timedelta(hours=2, minutes=1)})
    messages.extend(job_messages)
    with client:
        client.loop.run_until_complete(send_messages(messages))


def feed_the_toad():
    messages = []
    # Feed the toad
    time = datetime.today() + timedelta(minutes=2)
    messages.extend(prepare_message(time, 'покормить жабу', 'feed', toad_state, FEED_TOAD_PERIOD))
    with client:
        client.loop.run_until_complete(send_messages(messages))


async def send_messages(messages):
    sorted_messages = sorted(messages, key=lambda msg_time: msg_time['time'])
    messages = sorted_messages[0:MESSAGES_LIMIT]
    entity = await client.get_entity(BOYS_ID)
    for message in messages:
        await client.send_message(entity=entity, message=message['msg'], schedule=message['time'] - timedelta(hours=3))


toad_state_before = dict(toad_state)

feed_the_toad()
do_the_job()

if not toad_state_before == toad_state:
    with open("toad_state.json", "w") as write_file:
        ts = dict(feed=toad_state['feed'].timestamp(), job=toad_state['job'].timestamp())
        json.dump(ts, write_file)
