from metabase_api import Metabase_API
from importlib import import_module
from .rocketchat_manager import send_rc_message
import progressbar
import argparse
from concurrent.futures import ThreadPoolExecutor, as_completed
import os

class MetabaseQueryChecker:
    def __init__(self, settings_file_name):
        self.config = import_module(f"metabase_query_checker.{settings_file_name}")
        self.mb = Metabase_API(
            domain=self.config.METABASE_URL,
            email=self.config.METABASE_USERNAME,
            password=self.config.METABASE_PASSWORD
        )
        self.wanted_collections = self.config.WANTED_COLLECTIONS

    def create_progressbar(self, value):
        widgets = [' [',
                progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
                '] ',
                progressbar.Bar('*'),' (',
                progressbar.ETA(), ') ',
        ]

        bar = progressbar.ProgressBar(
            max_value=value, 
            widgets=widgets
        ).start()

        return bar

    def query_parser(self):
        cards = self.mb.get('/api/card', params={"f":"all"})
        
        filtered_cards = []
        # Filter cards to be analyzed
        if self.wanted_collections:
            for card in cards:
                collection_id = card['collection']['id'] if card['collection'] else None
                if collection_id in self.wanted_collections:
                    filtered_cards.append(card)
        else:
            filtered_cards = cards

        message = [
            f"Analyzing cards from {self.mb.domain}",
            f"{len(filtered_cards)} cards to be analyzed\n"
        ]
        bar = self.create_progressbar(len(filtered_cards))

        # Check if card is working
        card_map = {}
        
        def check_card(card):
            card_id = card['id']
            query_response = self.mb.post(f"/api/card/{card_id}/query")
            status = query_response['status']
            if status != 'completed':
                card_map[card_id] = {'status': status}

        def runner():
            threads = []
            with ThreadPoolExecutor(max_workers=os.cpu_count()) as executor:
                for i, card in enumerate(filtered_cards):
                    threads.append(executor.submit(check_card, card))
                for j, task in enumerate(as_completed(threads)):
                    bar.update(j)

        runner()

        if len(card_map) == 0:
            message.append("All clear! All cards worked fine!")
        else:
            for card_id, infos in card_map.items():
                message.append(
                    f"Card's of ID {card_id} status is {infos['status']}:"
                    f"click here {self.mb.domain}/card/{card_id} to correct"
                )

        return '\n'.join(message)


    def check_queries(self):
        message = self.query_parser()
        print(message) 
        try:
            send_rc_message(
                self.config,
                message,
                self.config.ROCKETCHAT_CHANNEL
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
    
    mb_qc = MetabaseQueryChecker(args.settings_file_name)
    mb_qc.check_queries()
