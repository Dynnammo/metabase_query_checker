from metabase_api import Metabase_API
from importlib import import_module
import json
import argparse
import re

class GraphMaker():
    def __init__(self, settings_file_name):
        self.config = import_module(f"metabase_query_checker.{settings_file_name}")
        self.mb = Metabase_API(
            domain=self.config.METABASE_URL,
            email=self.config.METABASE_USERNAME,
            password=self.config.METABASE_PASSWORD
        )
        self.wanted_collection = self.config.WANTED_COLLECTION
    
    def get_collection_graph(self):
        collections = self.mb.get('/api/collection')
        self.collection_graph = {}

        for collection in collections:
            c_id = str(collection['id'])
            c_location = collection.get('location') or ""
            c_name = collection['name']
            
            if 'Collection personnelle' not in c_name:
                self.collection_graph[c_id] = {}
                self.collection_graph[c_id]['name'] = c_name
                ancestors = list(filter(None, c_location.split('/')))
                ancestors.insert(0,'root')
                self.collection_graph[c_id]['ancestor'] = ancestors[-1]
                self.collection_graph[c_id]['all_ancestors'] = ancestors
        
        self.collection_graph.pop('root')
        
    def filter_collections(self):
        wanted_subgraph = {}
        wanted_collection_id = str(self.config.WANTED_COLLECTION)
        if wanted_collection_id:
            for collection_id, info in self.collection_graph.items():
                if wanted_collection_id == collection_id:
                    wanted_subgraph.update({collection_id: info})
                if wanted_collection_id in info['all_ancestors']:
                    wanted_subgraph.update({collection_id: info})
        self.collection_graph = wanted_subgraph
        

    def make_mermaid_graph_of_collections(self, file_name):
        from random import randint
        f = open(f'graph-{file_name}', 'w')
        f.write("graph LR\nroot(root)\n")
        
        # Define all objects
        for collection_id, info in self.collection_graph.items():
            f.write(f'{collection_id}("{info["name"]}")\n')
            
        # Define all links
        for collection_id, info in self.collection_graph.items():
            f.write(f"{info['ancestor']} --> {collection_id}\n")
            
        f.close()
    

def start():
    parser = argparse.ArgumentParser()
    parser.add_argument(
        'settings_file_name',
        type=str,
        help='Name of the settings file',
        default='settings'
    )
    args = parser.parse_args()
    
    mb_gm = GraphMaker(args.settings_file_name)
    mb_gm.get_collection_graph()
    mb_gm.filter_collections()
    mb_gm.make_mermaid_graph_of_collections(args.settings_file_name)
