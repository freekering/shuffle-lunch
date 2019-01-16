import datetime
import random
from slackclient import SlackClient

chunk_size = 6
slack_api_token = '' # bot user token required
notice_channel = '#announcement'
date = datetime.datetime.now().strftime('%Y-%m-%d')
random_seed = date.replace('-', '')
exclusion_status_text = '셔런불'
user_notice_templates = {
}

slack = SlackClient(slack_api_token)

slack.api_call(
    'chat.postMessage',
    channel=notice_channel,
    text=f":game_die: {date} 셔플 런치 추첨을 시작합니다! :game_die:"
)

response = slack.api_call('users.list')
all_users = list(
    filter(lambda user: not user['deleted'] and not user['is_bot'] and user['id'] != 'USLACKBOT', response['members'])
)
excluded_users = list(
    filter(lambda user: not user['is_restricted'] and user['profile']['status_text'] == exclusion_status_text, all_users)
)
for user in excluded_users:
    response = slack.api_call(
        'conversations.open',
        users=[user['id']]
    )
    if response['ok']:
        slack.api_call(
            'chat.postMessage',
            channel=response['channel']['id'],
            text=f'{user["real_name"]}님은 이번 셔플 런치에서 제외되셨습니다. 다음 셔플 런치를 기약해주시고 status 변경 잊지 말아주세요! :thanks:'
        )

target_users = list(
    filter(lambda user: not user['is_restricted'] and user['profile']['status_text'] == exclusion_status_text, all_users)
)


random.seed(random_seed)
random.shuffle(target_users)

n = len(target_users)
chunk_count = int(n / chunk_size)
remainder = n % chunk_size
if remainder > 0:
    chunk_count += 1

start = 0
for k in range(chunk_count):
    size = chunk_size
    if k >= chunk_count - (chunk_size - remainder):
        size -= 1
    selected_users = target_users[start:(start + size)]

    response = slack.api_call(
        'conversations.open',
        users=list(map(lambda user: user['id'], selected_users))
    )

    if response['ok']:
        channel = response['channel']['id']

        response = slack.api_call(
            'chat.postMessage',
            channel=channel,
            text=f':tada: {date} 셔플 런치 조가 생성되었습니다. 조장은 `{selected_users[0]["real_name"]}`님 입니다! :tada:'\
                  '\n(조장이 불가피한 사유로 불참 시 남은 분들 중에 선출해주세요)'
        )

        for user in selected_users:
            if user['id'] in user_notice_templates:
                slack.api_call(
                    'chat.postMessage',
                    channel=channel,
                    text=user_notice_templates[user['id']].format(user['real_name'])
                )

        if response['ok']:
            print('채널 생성 성공:')
        else:
            print('채널 생성 실패:')
    else:
        print('채널 생성 실패:')

    for user in selected_users:
        print(f'{user["id"]} {user["real_name"]}')
    print()

    start += size

slack.api_call(
    'chat.postMessage',
    channel=notice_channel,
    text=f"{date} 셔플 런치 추첨이 완료되었습니다! DM을 확인해주세요. :thanks:"
)
