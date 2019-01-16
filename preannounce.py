import config
from slackclient import SlackClient

if __name__ == "__main__":
    slack = SlackClient(config.SLACK_API_TOKEN)
    slack.api_call(
        'chat.postMessage',
        channel=config.NOTICE_CHANNEL,
        text=f'{config.START_TIME_FOR_PREANNOUNCE} {config.DATE} 셔플 런치 추첨이 시작됩니다.'\
             f'\n휴가 등의 불가피한 이유로 참석이 어려우신 분은 번거롭더라도 그 전까지 슬랙 status text를 `{config.EXCLUSION_STATUS_TEXT}`로 설정해주시면 추첨에서 자동으로 제외됩니다. :thanks:'
    )
