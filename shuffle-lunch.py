import random
from slackclient import SlackClient

slack_api_token = ''
random_seed = 0
chunk_size = 6
exclusion_emoji = None

slack = SlackClient(slack_api_token)

response = slack.api_call('users.list')
users = list(
    filter(lambda user: not user['deleted'] and not user['is_bot'] and user['id'] != 'USLACKBOT', response['members'])
)
users = list(
    filter(lambda user: not user['is_restricted'] and user['profile']['status_emoji'] != exclusion_emoji, users)
)

random.seed(random_seed)
random.shuffle(users)

n = len(users)
chunk_count = int(n / chunk_size)
remainder = n % chunk_size
if remainder > 0:
    chunk_count += 1

start = 0
for k in range(chunk_count):
    size = chunk_size
    if k >= chunk_count - (chunk_size - remainder):
        size -= 1
    selected_users = users[start:(start + size)]
    for u in selected_users:
        print(u['real_name'])
    print()
    start += size
