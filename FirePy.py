#! /usr/env/python

import sys
import os 
from os import system, name
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import glob
import json
import pandas as pd




#        File Name      : FirePy.py
#        Version        : v1.0
#        Author         : RpNull
#        Prerequisite   : Python3
#        Created        : 30 Sep 21
#        Change Date    : 12 Oct 21
#        Online version : github.com/RpNull/FirePy




load_dotenv()
api_pub=os.environ.get('PUB')
api_priv=os.environ.get('PRIV')
out_path=os.environ.get('OUTPATH')
app_name=os.environ.get('APP_NAME')
api_token=''
queries = 0



class Query():


    def query_paginated(url: str, xheaders) -> list:
        global queries
        responses = []
        while url:
            response = requests.get(url, headers = xheaders)
            responses.append(response.json())
            if not response.links or response.status_code == 204:
                print(f'Server Returned: {response.status_code}')
                break
            Admin.clear()
            url = response.links["next"]["url"]
            print(f'Sending Query: {url}\n')
            queries += 1
            print(f'Queries made: {queries}\n')
        return responses


    def indicator_query(query_days):
        global queries
        pathing = 'Indicators/'
        api_url = 'https://api.intelligence.fireeye.com/collections/indicators/objects'
        epoch = DataManager.epoch_fetch(query_days)
        ##APIv3 Limitation length:1000 for Indicators
        limit = 1000
        payload = {
            'added_after': f'{epoch}',
            'length': f'{limit}',
            'match.status': 'active'
        }
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
            }
        r = requests.get(api_url, headers=xheaders, params=payload)
        print(f'Sending Query: {r.request.url}')
        if r.status_code == 204:
                print('Query Complete')
        if r.status_code != 200:
                print(f'Server returned: {r.status_code}')
        if r.status_code == 200:
                data = r.json()
                api_url = r.links['next']['url']
                queries += 1
                print(f'Queries made: {queries}\n')
                data_extended = Query.query_paginated(api_url, xheaders)
                data_extended.append(data)
                DataManager.format_data(data_extended, pathing)
                


    def report_query(query_days):
        global queries
        pathing = 'Reports/'
        api_url = 'https://api.intelligence.fireeye.com/collections/reports/objects'
        epoch = DataManager.epoch_fetch(query_days)
        ##APIv3 Limitation length:100 for Reports
        limit = 100
        payload = {
            'added_after': f'{epoch}',
            'length': f'{limit}',
            'match.status': 'active'
        }
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
        }
        r = requests.get(api_url, headers=xheaders, params=payload)
        print(f'Sending Query: {r.request.url}')
        if r.status_code == 204:
                print('Query Complete')
        if r.status_code != 200:
                data = r.json()
                print(f'Server returned: {r.status_code}')
                print(data)                
        if r.status_code == 200:
                data = r.json()
                api_url = r.links['next']['url']
                queries += 1
                print(f'Queries made: {queries}\n')
                data_extended = Query.query_paginated(api_url, xheaders)
                data_extended.append(data)
                DataManager.format_data(data_extended, pathing)
                


    def alerts_query(query_days):
        global queries
        pathing = 'Alerts/'
        api_url = 'https://api.intelligence.fireeye.com/collections/alerts/objects'
        epoch = DataManager.epoch_fetch(query_days)
        ##APIv3 Limitation length:100 for Alerts
        limit = 100
        payload = {
            'added_after': f'{epoch}',
            'length': f'{limit}',

        }
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
            }
        r = requests.get(api_url, headers=xheaders, params=payload)
        print(f'Sending Query: {r.request.url}')
        if r.status_code == 204:
                print('Query Complete')
        if r.status_code != 200:
                print(f'Server returned: {r.status_code}')
        if r.status_code == 200:
                data = r.json()
                api_url = r.links['next']['url']
                queries += 1
                print(f'Queries made: {queries}\n')
                data_extended = Query.query_paginated(api_url, xheaders)
                data_extended.append(data)
                DataManager.format_data(data_extended, pathing)


    def permissions_query():
        api_url = 'https://api.intelligence.fireeye.com/permissions'
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
        }
        r = requests.get(api_url, headers=xheaders)
        data = r.json()
        print(f'Permissions for {api_token}:\n{data}\n\n\n')
        input("Press any key to return to main menu.\n")
    


class DataManager():


     def token():
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


     def epoch_fetch(query_days) -> str:
        d = datetime.now()
        p = str((d - timedelta(days=query_days)).timestamp())
        return p

     
     def format_data(data, pathing):
        global queries

        d = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_file = f"{out_path}{pathing}{d}.json"

        print(f'Saving to: {out_file}\n\n\n')
        try:
            with open(out_file, 'w') as f:
                    json.dump(data, f)
            input("Press any key to return to main menu.\n")
        except Exception as e:
            print(e)
            print(f'Writing to {out_path} failed, please check permissions and write locks.')



class Admin():


    def merge():
        extensions = 'csv'
        os.chdir(f'{out_path}/Indicators/')
        all_files = [ i for i in glob.glob('*.{}'.format(extensions))]
        combined_csv = pd.concat([pd.read_csv(f) for f in all_files ])
        combined_csv.to_csv( "Combined_Indicators.csv", index=False, encoding='utf-8-sig')
        os.chdir(f'{out_path}/Reports/')
        all_files = [ i for i in glob.glob('*.{}'.format(extensions))]
        combined_csv = pd.concat([pd.read_csv(f) for f in all_files ])
        combined_csv.to_csv( "Merged_Reports.csv", index=False, encoding='utf-8-sig')
        os.chdir(f'{out_path}/Alerts/')
        all_files = [ i for i in glob.glob('*.{}'.format(extensions))]
        combined_csv = pd.concat([pd.read_csv(f) for f in all_files ])
        combined_csv.to_csv( "Merged_Alerts.csv", index=False, encoding='utf-8-sig')


    def clear():  
        # for windows
        if name == 'nt':
            _ = system('cls')  
        # for mac and linux(here, os.name is 'posix')
        else:
            _ = system('clear')


    def stats_tracker():
        d = datetime.now().strftime("%Y%m%d")
        file_size_total = (os.path.getsize(f"{out_path}Reports/")-4096)
        file_size_total += os.path.getsize(f"{out_path}Indicators/")
        file_size_total += os.path.getsize(f"{out_path}Alerts/")
        qd = 50000 - queries
        Admin.clear()
        print(
            f'''
            Queries this session: {queries}\n
            Queries remaining today: {qd}\n
            Total Data pulled: {file_size_total}\n
            Files Written to: {out_path}\n
        ''')
        
    
    def path_check():
        r = os.path.isdir(f'{out_path}Reports')
        i = os.path.isdir(f'{out_path}Indicators')
        a = os.path.isdir(f'{out_path}Alerts')
        if r is False:
            os.mkdir(f'{out_path}Reports')
        if i is False:
            os.mkdir(f'{out_path}Indicators')
        if a is False:
            os.mkdir(f'{out_path}Alerts')


    def menu():
        looping = True
        while looping:
            Admin.stats_tracker()
            choice=input(
                '''
                1) Query Indicators Endpoint\n
                2) Query Reports Endpoint\n
                3) Query Alerts Endpoint\n
                4) Query Permissions Endpoint (Troubleshooting)\n
                5) Merge CSVs, Exit\n
                X) Exit program\n
                '''
            )
            if choice == '1':
                Admin.clear()
                query_days = int(input('How many days would you like to query? \n'))
                try:
                    Query.indicator_query(query_days)
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '2':
                Admin.clear()
                query_days = int(input('How many days would you like to query? \n'))
                try:
                    Query.report_query(query_days)
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '3':
                Admin.clear()
                query_days = int(input('How many days would you like to query? \n'))
                try:
                    Query.alerts_query(query_days)
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '4':
                Admin.clear()
                try:
                    Query.permissions_query()
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '5':
                Admin.clear()
                try:
                    Admin.merge()
                    sys.exit(0)
                except Exception as e:
                    print(e)
                    print(f'Merge failed.')
            elif choice == 'X':
                looping = False
                print(f'Exiting.\n')
                sys.exit(0)
            else:
                print(f'{choice} is not a valid option, please make a selection\nNote: "X" must be capitalized to exit 😉\n\n\n')
                input("Press any key to return to main menu.\n")



def main():
    Admin.path_check()
    try:
        exp = DataManager.token()
    except:
        print(f'Unable to fetch token, please confirm required variables are placed in your .env file')
        sys.exit(0)
    print(f'Token expires in {exp} hours\n')
    Admin.menu()



main()