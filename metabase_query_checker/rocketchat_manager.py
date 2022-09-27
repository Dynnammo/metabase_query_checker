from requests import sessions
from rocketchat_API.rocketchat import RocketChat
from dotenv import dotenv_values

config = dotenv_values()

def send_rc_message(config, message, channel):
    with sessions.Session() as session:
        rocket = RocketChat(
            config['ROCKETCHAT_USERNAME'],
            config['ROCKETCHAT_PASSWORD'],
            server_url=config['ROCKETCHAT_URL'],
            session=session
        )

    rocket.chat_post_message(
        message,
        channel=channel
    )
