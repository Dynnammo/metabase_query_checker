from metabase_api import Metabase_API
from importlib import import_module
from .rocketchat_manager import send_rc_message
import progressbar
import argparse


def connect(config):
    mb = Metabase_API(
        domain=config.METABASE_URL,
        email=config.METABASE_USERNAME,
        password=config.METABASE_PASSWORD
    )
    return mb

def create_progressbar(mb):
    widgets = [' [',
            progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
            '] ',
            progressbar.Bar('*'),' (',
            progressbar.ETA(), ') ',
    ]

    bar = progressbar.ProgressBar(
        max_value=len(mb.get('/api/card', params={"f":"all"})), 
        widgets=widgets
    ).start()

    return bar

def query_parser(bar, mb, ignored_collections=[]):
    response = mb.get('/api/card', params={"f":"all"})
    message = [
        f"Analyzing cards from {mb.domain}",
        f"{len(response)} cards to be analyzed\n"
    ]

    card_map = {}
    for i, card in enumerate(response):
        card_id = card['id']
        query_response = mb.post(f"/api/card/{card_id}/query")
        status = query_response['status']
        if status != 'completed':
            collection = mb.get(f"/api/card/{card_id}").get('collection')
            collection_name = collection.get('name') if collection is not None else ''
            if collection_name not in ignored_collections:
                card_map[card_id] = {'status': status}
        bar.update(i)

    if len(card_map) == 0:
        message.append("All clear! All cards worked fine!")
    else:
        for card_id, infos in card_map.items():
            message.append(
                f"Card's of ID {card_id} status is {infos['status']}:"
                f"click here {mb.domain}/card/{card_id} to correct"
            )

    return '\n'.join(message)

def check_queries(settings_file_name):
    config = import_module(f"metabase_query_checker.{settings_file_name}")
    mb = connect(config)
    widget_progress_bar = create_progressbar(mb)
    message = query_parser(
        widget_progress_bar,
        mb,
        config.IGNORED_COLLECTIONS
    )
    print(message)
    try:
        send_rc_message(
            config,
            message,
            config.ROCKETCHAT_CHANNEL
        )
        print("Sending notification to Rocket.Chat worked!")
    except Exception:
        print("Sending notification failed")

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'settings_file_name',
        type=str,
        help='Name of the settings file',
        default='settings'
    )
    args = parser.parse_args()
    
    check_queries(args.settings_file_name)
