#! /usr/env/python
import os, requests, json, sys, csv
import pandas as pd
import pprint
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dotenv import load_dotenv
#        File Name      : FirePy.py
#        Version        : v.0.1
#        Author         : RpNull
#        Prerequisite   : Python3
#        Created        : 30 Sep 21
#        Change Date    : 6 Oct 21
#        Online version : github.com/RpNull/FirePy

load_dotenv()
api_pub=os.environ.get('PUB')
api_priv=os.environ.get('PRIV')
out_path=os.environ.get('OUTPATH')
app_name=os.environ.get('APP_NAME')
api_token=''

class Query():    
   
    def Indicator_Query(query_days):
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
        epoch = DataManager.Epoch_Fetch(query_days)
        ##APIv3 Limitation length:1000 for Indicators
        payload = {
            'added_after': 'epoch',
            'length': '1000',
            'match_status': 'active'
        }
        print(f'{api_token}')
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
            }
        print(f'{xheaders}')
        r = requests.get(api_url, headers=xheaders, data=payload)
        if r.status_code != 200:
            raise Exception(r.text)
        if r.status_code == 200:
            data = r.json()
            df = pd.json_normalize(data["objects"])
            df[formatting]
           # DataManager.Format_Data(data, formatting, pathing)

    def Report_Query(query_days):
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
        epoch = DataManager.Epoch_Fetch(query_days)
        ##APIv3 Limitation length:100 for Reports
        payload = {
            'added_after': '{epoch}',
            'length': '100',
            'match_status': 'active'
        }

        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
            }

        r = requests.get(api_url,headers=xheaders,data=payload)
        if r.status_code != 200:
            raise Exception(r.text)
        if r.status_code == 200:
            data = r.json()
            DataManager.Format_Data(data, formatting, pathing)

    def Permissions_Query():
        api_url = 'https://api.intelligence.fireeye.com/permissions'
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': 'f{app_name}',
            'Authorization': f'Bearer {api_token}'
            }
        r = requests.get(api_url, headers=xheaders)
        data = r.json
        print(f'{data}')

class DataManager():

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
        p = data.get("token_type")
        print(f'Token Type: {p}\nToken Value = {api_token}')
        return(token_expire)

     def Epoch_Fetch(query_days):
        d = datetime.now()
        p = str((d - timedelta(days=query_days)).timestamp())
        return p

     
     def Format_Data(data, formatting, pathing):
        named_list = []
        for name in data['Objects']:
            named_list.append(data['Name'])

        dataset = pd.DataFrame(data, columns = formatting)
        #dataset.columns = formatting
        dataset.index = pd.RangeIndex(len(dataset.index))
        d = str(datetime.now())
        out_file = out_path + pathing + d
        try:
            dataset.to_csv(out_file, True)
        except:
            print(f'Writing to {out_path} failed, please check permissions and write locks.')
class Admin():
    def menu():
        looping = True
        while looping:
            choice=input(
                '''1) Query Indicators\n
                2) Query Reports \n
                3) Query <PLACEHOLDER>\n
                x) Exit program\n
                '''
            )
            if choice == '1':
                query_days = int(input('How many days would you like to query? \n'))
                try:
                    Query.Indicator_Query(query_days)
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '2':
                query_days = input('How many days would you like to query? \n')
                try:
                    Query.Report_Query()
                except:
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '3':
                try:
                    Query.Permissions_Query()
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == 'X':
                looping = False
                print(f'Exiting.\n')
                sys.exit(0)
            else:
                print(f'{choice} is not a valid option, please make a selection\n')

def main():
    try:
        exp = DataManager.Token()
    except:
        print(f'Unable to fetch token, please confirm required variables are placed in your .env file')
        sys.exit(0)
    print(f'Token expires in {exp} hours\n')
    Admin.menu()


main()

