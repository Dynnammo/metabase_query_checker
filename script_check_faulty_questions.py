from metabase_api import Metabase_API
from pprint import pp
from dotenv import dotenv_values
import progressbar

config = dotenv_values()

widgets = [' [',
         progressbar.Timer(format= 'elapsed time: %(elapsed)s'),
         '] ',
           progressbar.Bar('*'),' (',
           progressbar.ETA(), ') ',
]


mb = Metabase_API(
    domain=config['METABASE_URL'],
    email=config['METABASE_USERNAME'],
    password=config['METABASE_PASSWORD']
)

response = mb.get('/api/card', params={"f":"all"})
print(f"{len(response)} cards to be analyzed")

bar = progressbar.ProgressBar(max_value=200, 
                              widgets=widgets).start()

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
