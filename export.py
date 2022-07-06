import json
from os import path

# https://pypi.org/project/dhis2.py/
from dhis2 import Api, clean_obj, setup_logger, logger

from slugify import slugify

# create the Api object with credentials from auth.json
api = Api.from_auth_file('auth.json')

# set up the logger
setup_logger()

# specify the dict keys we want to remove for cleaner files
default_remove_keys = [
    'lastUpdatedBy',
    'user',
    'path'
]

def save_json(data, filename, remove_keys=default_remove_keys):
    """Save JSON file to a folder"""
    data = clean_obj(data, remove_keys)
    file_path = path.join('metadata', f"{filename}.json")
    with open(file_path, 'w') as f:
        json.dump(data, f, indent=2)
    logger.info(f"Saved file: {file_path}")
    

def export_orgunits():
    data = api.get_paged('organisationUnits', params={'fields': ':owner'}, page_size=1000, merge=True)
    save_json(data, '1_organisation_units')

def export_data_sets():
    data_sets = {d['id']: d['name'] for d in api.get('dataSets', params={'fields': 'id,name'}).json().get('dataSets')}
    for uid, name in data_sets.items():
        logger.info("Found data sets:")
        logger.info(f" - {name} ({uid})")
        data = api.get(f'dataSets/{uid}/metadata').json()
        slug_name = f"2_dataset_{slugify(name)}_{uid}"
        save_json(data, slug_name)


def main():
    logger.info(f"Starting export of configuration from {api.base_url}")
    export_orgunits()
    export_data_sets()

if __name__ == '__main__':
    main()