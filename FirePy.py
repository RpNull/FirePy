#! /usr/env/python

import os, requests, json, sys, glob
from os import system, name
import pandas as pd
from requests.auth import HTTPBasicAuth
from datetime import datetime, timedelta
from dotenv import load_dotenv
#        File Name      : FirePy.py
#        Version        : v.0.12
#        Author         : RpNull
#        Prerequisite   : Python3
#        Created        : 30 Sep 21
#        Change Date    : 8 Oct 21
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
        output_list = []
        while url:
            response = requests.get(url, headers = xheaders)
            data = response.json()
            output_list.extend(data.get("objects", []))
            if not response.links or response.status_code == 204:
                print(f'Server Returned: {response.status_code}')
                break
            Admin.clear()
            url = response.links["next"]["url"]
            print(f'Sending Query: {url}\n')
            queries += 1
            stat = len(output_list)
            print(f'Queries made: {queries}\nObjects retrieved: {stat}')
        return output_list


    def Indicator_Query(query_days):
        global queries
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
        pathing = 'Indicators/'
        api_url = 'https://api.intelligence.fireeye.com/collections/indicators/objects'
        epoch = DataManager.Epoch_Fetch(query_days)
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
                objects = data['objects']
                api_url = r.links['next']['url']
                queries += 1
                cobj = len(objects)
                print(f'Queries made: {queries}\nObjects retrieved: {cobj}\n')
                object_list = Query.query_paginated(api_url, xheaders)
                objects.extend(object_list)
                DataManager.Format_Data(objects, formatting, pathing)


    def Report_Query(query_days):
        global queries
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
                queries += 1
                data = r.json()
                objects = data['objects']
                api_url = r.links['next']['url']
                queries += 1
                cobj = len(objects)
                print(f'Queries made: {queries}\nObjects retrieved: {cobj}\n')
                object_list = Query.query_paginated(api_url, xheaders)
                objects.extend(object_list)
                DataManager.Format_Data(objects, formatting, pathing)
        

    def Permissions_Query():
        api_url = 'https://api.intelligence.fireeye.com/permissions'
        xheaders = {
            'Accept': 'application/stix+json; version=2.1',
            'X-App-Name': f'{app_name}',
            'Authorization': f'Bearer {api_token}'
        }
        r = requests.get(api_url, headers=xheaders)
        data = r.json()
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
        global queries
        dataset = pd.DataFrame(data)
        d = datetime.now().strftime("%Y%m%d-%H%M%S")
        out_file = f"{out_path}{pathing}{d}.csv"

        print(f'Saving to: {out_file}\n')
        try:
            dataset.to_csv(out_file)
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
        file_size_total = (os.path.getsize(f"{out_path}Indicators/")-4096)
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
        if r is False:
            os.mkdir(f'{out_path}/Reports')
        if i is False:
            os.mkdir(f'{out_path}/Indicators')
    

    def menu():
        looping = True
        while looping:
            Admin.stats_tracker()
            choice=input(
                '''
                1) Query Indicators\n
                2) Query Reports\n
                3) Query Permissions (Troubleshooting)\n
                4) Merge CSVs, Exit\n
                X) Exit program\n
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
                query_days = int(input('How many days would you like to query? \n'))
                try:
                    Query.Report_Query(query_days)
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '3':
                try:
                    Query.Permissions_Query()
                except Exception as e:
                    print(e)
                    print('Query failed, please confirm API keys and enviromental variables. Exiting\n')
            elif choice == '4':
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
                print(f'{choice} is not a valid option, please make a selection\nNote: "X" must be capitalized to exit 😉:')




def main():
    Admin.path_check()
    try:
        exp = DataManager.Token()
    except:
        print(f'Unable to fetch token, please confirm required variables are placed in your .env file')
        sys.exit(0)
    print(f'Token expires in {exp} hours\n')
    Admin.menu()



main()