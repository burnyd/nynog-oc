import requests, json

requests.packages.urllib3.disable_warnings()

def get_json():
    headers = {'Content-Type': 'application/json', 'Accept': 'application/json'}
    api_call = 'http://127.0.0.1:5000/static/ceos1_bgp.json'
    result = requests.get(api_call, headers=headers, verify=False)
    #print(result.text)
    print(json.dumps(result.text).encode())

get_json()

