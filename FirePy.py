import os, requests, json
import pandas as pd
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta

api_pub=os.getenv('PUB')
api_priv=os.getenv('PRIV')
out_path=os.getenv('OUTPATH')
app_name=os.getenv('APP_NAME')
api_token=''
qeury_days=''

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
        p = str((d - timedelta(days=query_days)).timestamp())
        return p
   
    def Indicator_Query():
        formatting = [
            "id", 
            "name",
            "created", 
            "modified",
            "valid_from", 
            "valid_until", 
            "confidence",
            "description", 
            "pattern", 
            "labels"
        ]
        pathing = 'Indicator/'
        api_url = 'https://api.intelligence.fireeye.com/collections/indicators/objects'
        epoch = Query.Epoch_Fetch()
        ##APIv3 Limitation length:1000 for Indicators
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
            DataManager.Format_Data(data, formatting, pathing)

    def Report_Query():
        formatting =  [
            "id", 
            "name", 
            "labels", 
            "created", 
            "modified", 
            "published", 
            "object_refs", 
            "description", 
            "x_fireeye_com_tracking_info.document_id", 
            "x_fireeye_com_metadata.report_type", 
            "x_fireeye_com_metadata.affected_it_systems", 
            "x_fireeye_com_metadata.risk_rating", 
            "x_fireeye_com_exploitation_rating", 
            "x_fireeye_com_metadata.intended_effect", 
            "x_fireeye_com_additional_description_sections.analysis", 
            "x_fireeye_com_metadata.target_geographies", 
            "x_fireeye_com_metadata.affected_industries", 
            "x_fireeye_com_additional_description_sections.key_points", 
            "x_fireeye_com_metadata.targeted_information", 
            "x_fireeye_com_metadata.motivation", 
            "x_fireeye_com_metadata.subscriptions", 
            "x_fireeye_com_metadata.source_geographies", 
            "x_fireeye_com_risk_rating_justification", 
            "x_fireeye_com_metadata.affected_ot_systems"
        ]
        pathing = 'Reports/'
        api_url = 'https://api.intelligence.fireeye.com/collections/reports/objects'
        epoch = Query.Epoch_Fetch()
        ##APIv3 Limitation length:100 for Reports
        payload = {
            'added_after': '{epoch}',
            'length': '100',
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
            DataManager.Format_Data(data, formatting, pathing)


class DataManager():
     
     def Format_Data(data, formatting, pathing):
        dataset = pd.DataFrame(data)
        dataset.columns = formatting
        dataset.index = pd.RangeIndex(len(dataset.index))
        d = str(datetime.now())
        out_file = out_path + pathing + d
        try:
            dataset.to_csv(out_file, True)
        except:
            print(f'Writing to {out_path} failed, please check permissions and write locks.')


def menu():
    global query_days
    looping = True
    while looping:
        choice=str(input(
            '''1) Query Indicators\n
            2) Query Reports \n
            3) Query <PLACEHOLDER>\n
            x) Exit program\n
            '''
        )).capitalize
        if choice == 1:
            query_days = input('How many days would you like to query? \n')
            try:
                Query.Indicator_Query()
            except:
                print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
        elif choice == 2:
            query_days = input('How many days would you like to query? \n')
            try:
                Query.Report_Query()
            except:
                print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
        elif choice == 'X':
            looping = False
            print(f'Exiting.\n')
            sys.exit(0)
        else:
            print(f'{choice} is not a valid option, please make a selection\n')

def main():
    try:
        exp = Query.Token()
    except:
        print(f'Unable to fetch token, please confirm required variables are placed in your .env file')
        sys.exit(0)
    print(f'Token expires in {exp} hours\n')
    menu()
