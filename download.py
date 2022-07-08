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
    'path',
    'createdBy'
]

def save_json(data, filename, remove_keys=default_remove_keys):
    """Save JSON file to a folder"""
    if data:
        data = clean_obj(data, remove_keys)
        file_path = path.join('metadata', f"{filename}.json")
        with open(file_path, 'w') as f:
            json.dump(data, f, indent=2)
        logger.info(f"Saved file: {file_path}")
    

def download_orgunits():
    data = {}
    data['organisationUnits'] = api.get_paged('organisationUnits', params={'fields': ':owner'}, page_size=1000, merge=True)['organisationUnits']
    data['organisationUnitLevels'] = api.get('organisationUnitLevels', params={'fields': ':owner'}).json()['organisationUnitLevels']
    save_json(data, '1_organisation_units')

def download_data_sets():
    data_sets = {d['id']: d['name'] for d in api.get('dataSets', params={'fields': 'id,name'}).json().get('dataSets')}
    logger.info(f"Found {len(data_sets)} datasets")
    for uid, name in data_sets.items():
        logger.info(f" - {name} ({uid})")
        data = api.get(f'dataSets/{uid}/metadata').json()
        # remove org unit association
        data['dataSets'][0]['organisationUnits'] = []
        slug_name = f"2_dataset_{slugify(name)}_{uid}"
        save_json(data, slug_name)

def download_dashboards():
    dashboards = {d['id']: d['name'] for d in api.get('dashboards', params={'fields': 'id,name'}).json().get('dashboards')}
    logger.info(f"Found {len(dashboards)} dashboards")
    for uid, name in dashboards.items():
        logger.info(f" - {name} ({uid})")
        data = api.get(f'dashboards/{uid}/metadata').json()
        slug_name = f"9_dashboard_{slugify(name)}_{uid}"
        save_json(data, slug_name)


def download_user_config():
    data = {}
    user_roles = api.get('userRoles', params={'fields': ':owner'}).json()['userRoles']
    user_groups = api.get('userGroups', params={'fields': ':owner'}).json()['userGroups']
    data['userRoles'] = user_roles
    data['userGroups'] = user_groups
    # remove users from the group
    for ug in data['userGroups']:
        ug['users'] = []
    save_json(data, '1_user_config')


def main():
    logger.info(f"Starting export of configuration from {api.base_url}")
    download_orgunits()
    download_data_sets()
    download_dashboards()
    download_user_config()

if __name__ == '__main__':
    main()