from dhis2 import Api

api = Api.from_auth_file('auth.json')

print(api.info)