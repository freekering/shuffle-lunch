import datetime
import random
from slackclient import SlackClient

chunk_size = 6
slack_api_token = '' # bot user token required
date = datetime.datetime.now().strftime('%Y-%m-%d')
random_seed = date.replace('-', '')
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

    response = slack.api_call(
        'conversations.open',
        users=list(map(lambda user: user['id'], selected_users))
    )

    if response['ok']:
        response = slack.api_call(
            'chat.postMessage',
            channel=response['channel']['id'],
            text=f':tada: {date} 셔플 런치 조가 생성되었습니다. 조장은 `{selected_users[0]["real_name"]}`님 입니다! :tada:'\
                  '\n(조장이 불가피한 사유로 불참 시 남은 분들 중에 선출해주세요)',
            as_user=True
        )
        if response['ok']:
            print('채널 생성 성공:')
        else:
            print('채널 생성 실패:')
    else:
        print('채널 생성 실패:')

    for user in selected_users:
        print(user['real_name'])
    print()

    start += size
