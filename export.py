from dhis2 import Api, pretty_json

api = Api.from_auth_file('auth.json')

pretty_json(api.info)