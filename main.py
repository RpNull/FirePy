import os, requests, json
import pandas as pd
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

api_pub=os.getenv('PUB')
api_priv=os.getenv('PRIV')
out_path=os.getenv('PATH')
app_name=os.getenv('APP_NAME')
api_token=''

class Query():    
    def Token():
        global api_token
        api_url="https://api.intelligence.fireeye.com/token"
        headers = {
            'grant_type' : 'client_credentials'
        }
        r = requests.post(api_url, auth=HTTPBasicAuth(api_pub, api_priv), data=headers)
        data = r.json()
        api_token = data.get('access_token')
        token_expire = divmod(data.get('expires_in'), 3600)
        return(token_expire)

    def Epoch_Fetch():
        d = datetime.now()
        p = (d - timedelta(days=90)).timestamp()
        return p

    def Format_Data(data):
        dataset = pd.DataFrame(data)
        dataset.columns = ["id", "name", "created", "modified", "valid_from", "valid_until", "confidence", "description", "pattern", "labels"]
        dataset.index = pd.RangeIndex(len(dataset.index))
        d = str(datetime.now())
        out_file = out_path + d
        dataset.to_csv(out_file, True)

    def Indicator_Query():
        api_url = 'https://api.intelligence.fireeye.com/collections/indicators/objects'
        epoch = Query.Epoch_Fetch()
        payload = {
            'added_after': '{epoch}',
            'length': '1000',
            'match_status': 'active'
        }

        headers = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': '{app_name}',
            'Authorization': 'Bearer {auth_token}'
            }

        r = requests.get(api_url,headers,payload)
        if r.status_code != 200:
            raise Exception(r.text)
        if r.status_code == 200:
            data = r.json()
            Query.Format_Data(data)

def main():
    exp = Query.Token()
    print(f'Token expires in {exp} hours')
    try:
        Query.Indicator_Query()
    except:
        print(f'Query Failed')





