from metabase_api import Metabase_API
from pprint import pp
from dotenv import dotenv_values
import progressbar


def connect():
    config = dotenv_values()
    mb = Metabase_API(
        domain=config['METABASE_URL'],
        email=config['METABASE_USERNAME'],
        password=config['METABASE_PASSWORD']
    )
    return mb

def create_progressbar():
    widgets = [' [',
            progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
            '] ',
            progressbar.Bar('*'),' (',
            progressbar.ETA(), ') ',
    ]

    bar = progressbar.ProgressBar(
        max_value=200, 
        widgets=widgets
    ).start()

    return bar

def query_parser(bar, mb):
    response = mb.get('/api/card', params={"f":"all"})
    print(f"{len(response)} cards to be analyzed")

    for i, card in enumerate(response):
        card_id = card['id']
        status = (mb.post(f"/api/card/{card_id}/query"))['status']
        card_map = {}
        if status != 'completed':
            card_map[card_id] = status
        bar.update(i)

    if len(card_map) == 0:
        print("All clear! All cards worked fine")
    else:
        for card_id, status in card_map.items():
            print(f"Card's status is {status}: click here {mb.domain}/card/{card_id} to correct")

def check_queries():
    mb = connect()
    widget_progress_bar = create_progressbar()
    query_parser(widget_progress_bar, mb)