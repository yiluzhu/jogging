import json
import requests

host = 'http://localhost:5000/'


# 0. create admin user by running utils.py and copy admin token below.
admin_token = '93ad94bd-e8b7-4ca3-b56a-9f5c7444bf88'


print('1. create stuff user')
payload = {'email': '', 'forename': 'Alex', 'surname': 'Zhu', 'username': 'alexzhu', 'password': 'aaa111', 'role': 'staff'}
requests.put(host + 'user', data=json.dumps(payload), headers={'content-type': 'application/json', 'Authorization': admin_token})
input('Press any key to continue...')


print('2. login staff user')
payload = {'username': 'alexzhu', 'password': 'aaa111'}
resp = requests.post(host + 'login', data=json.dumps(payload), headers={'content-type': 'application/json'})
staff_token = resp.json()['token']
input('Press any key to continue...')


print('3. create user Tony')
payload = {'email': '', 'forename': 'Tony', 'surname': 'Smith', 'username': 'tonysmith', 'password': 'ttt111'}
requests.put(host + 'user', data=json.dumps(payload), headers={'content-type': 'application/json', 'Authorization': staff_token})
input('Press any key to continue...')


print('4. create user Lucy')
payload = {'email': '', 'forename': 'Lucy', 'surname': 'Smith', 'username': 'lucysmith', 'password': 'uuu111'}
requests.put(host + 'user', data=json.dumps(payload), headers={'content-type': 'application/json', 'Authorization': staff_token})
input('Press any key to continue...')


print('5. Tony login')
payload = {'username': 'tonysmith', 'password': 'ttt111'}
resp = requests.post(host + 'login', data=json.dumps(payload), headers={'content-type': 'application/json'})
tony_token = resp.json()['token']
input('Press any key to continue...')


print('6. Tony create 3 records')
payloads = [
    {'date': '2020-09-27', 'distance': 9369, 'lat': 38.7, 'lon': 46.2, 'time': 25, 'username': 'tonysmith'},
    {'date': '2020-09-28', 'distance': 8251, 'lat': -26.2, 'lon': -82.0, 'time': 10, 'username': 'tonysmith'},
    {'date': '2020-09-29', 'distance': 7572, 'lat': 37.8, 'lon': -145.6, 'time': 7, 'username': 'tonysmith'},
]
for p in payloads:
    requests.put(host + 'record', data=json.dumps(p), headers={'content-type': 'application/json', 'Authorization': tony_token})
input('Press any key to continue...')


print('7. Lucy create 3 records')
payloads = [
    {'date': '2020-09-27', 'distance': 3979, 'lat': -8.3, 'lon': 37.9, 'time': 13, 'username': 'lucysmith'},
    {'date': '2020-09-28', 'distance': 5131, 'lat': 51.0, 'lon': -119.8, 'time': 29, 'username': 'lucysmith'},
    {'date': '2020-09-29', 'distance': 8743, 'lat': 27.1, 'lon': 19.9, 'time': 43, 'username': 'lucysmith'},
]
for p in payloads:
    requests.put(host + 'record', data=json.dumps(p), headers={'content-type': 'application/json', 'Authorization': admin_token})
input('Press any key to continue...')


print('8. Tony make weekly report')
resp = requests.get(host + 'report', headers={'content-type': 'application/json', 'Authorization': tony_token})
print(resp.json()['data'])
input('Press any key to continue...')


print('9. Tony read records to get ids')
resp = requests.get(host + 'record', headers={'content-type': 'application/json', 'Authorization': tony_token})
print(resp.json()['data'])
input('Press any key to continue...')


print('10. Tony update record')
payload = {'rid': 1, 'distance': 100, 'time': 30, 'username': 'tonysmith'}
resp = requests.post(host + 'record', data=json.dumps(payload), headers={'content-type': 'application/json', 'Authorization': tony_token})
input('Press any key to continue...')


print("11. delete all Lucy's records")
for i in [4, 5, 6]:
    requests.delete(host + f'record/{i}', headers={'content-type': 'application/json', 'Authorization': admin_token})
input('Press any key to continue...')


print('12. delete user Lucy')
requests.delete(host + 'user/lucysmith', headers={'content-type': 'application/json', 'Authorization': admin_token})
input('Press any key to continue...')


print('13. Tony logout')
requests.get(host + 'logout', headers={'content-type': 'application/json', 'Authorization': tony_token})
input('Press any key to continue...')
