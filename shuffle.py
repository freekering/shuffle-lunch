import config
import datetime
import random
from slackclient import SlackClient

def pre_message(slack):
    slack.api_call(
        'chat.postMessage',
        channel=config.NOTICE_CHANNEL,
        text=f":game_die: {config.DATE} 셔플 런치 추첨을 시작합니다! :game_die:"
    )

def fetch_users(slack):
    users_list_response = slack.api_call('users.list')
    all_users = list(
        filter(lambda user: not user['deleted'] and not user['is_bot'] and user['id'] != 'USLACKBOT', users_list_response['members'])
    )
    excluded_users = list(
        filter(lambda user: not user['is_restricted'] and user['profile']['status_text'] == config.EXCLUSION_STATUS_TEXT, all_users)
    )
    target_users = list(
        filter(lambda user: not user['is_restricted'] and user['profile']['status_text'] != config.EXCLUSION_STATUS_TEXT, all_users)
    )
    return (target_users, excluded_users)

def post_exclusion_message(slack, excluded_users):
    for user in excluded_users:
        response = slack.api_call(
            'conversations.open',
            users=[user['id']]
        )
        if response['ok']:
            slack.api_call(
                'chat.postMessage',
                channel=response['channel']['id'],
                text=f'{user["real_name"]}님은 이번 셔플 런치에서 제외되셨습니다. 다음 셔플 런치를 기약해주시고 슬랙 status text 변경 잊지 말아주세요! :thanks:'
            )

def shuffle(slack, target_users):
    random.seed(config.RANDOM_SEED)
    random.shuffle(target_users)

    n = len(target_users)
    chunk_count = int(n / config.CHUNK_SIZE)
    remainder = n % config.CHUNK_SIZE
    if remainder > 0:
        chunk_count += 1

    start = 0
    for k in range(chunk_count):
        size = config.CHUNK_SIZE
        if k >= chunk_count - (config.CHUNK_SIZE - remainder):
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
                text=f':tada: {config.DATE} 셔플 런치 조가 생성되었습니다. 조장은 `{selected_users[0]["real_name"]}`님 입니다! :tada:'\
                    '\n(조장이 불가피한 사유로 불참 시 남은 분들 중에 선출해주세요)'
            )

            for user in selected_users:
                if user['id'] in config.USER_SPECIFIC_NOTICE_TEMPLATES:
                    slack.api_call(
                        'chat.postMessage',
                        channel=channel,
                        text=config.USER_SPECIFIC_NOTICE_TEMPLATES[user['id']].format(user['real_name'])
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

def post_message(slack):
    slack.api_call(
        'chat.postMessage',
        channel=config.NOTICE_CHANNEL,
        text=f"{config.DATE} 셔플 런치 추첨이 완료되었습니다! DM을 확인해주세요. :thanks:"
    )

if __name__ == "__main__":
    slack = SlackClient(config.SLACK_API_TOKEN)
    pre_message(slack)
    target_users, excluded_users = fetch_users(slack)
    post_exclusion_message(slack, excluded_users)
    shuffle(slack, target_users)
    post_message(slack)
