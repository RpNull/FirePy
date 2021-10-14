import sys
import os
import argparse
import logging 
from dotenv import load_dotenv
from datetime import datetime, timedelta
import requests
from requests.auth import HTTPBasicAuth
import json
from keys import misp_url, misp_key, misp_verifycert
from pymisp import ExpandedPyMISP



#        File Name      : MisPy.py
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

#Initialize misp instance & logging
misp=ExpandedPyMISP(misp_url, misp_key, misp_verifycert)
logging.basicConfig(filename='/var/log/Firepy/log.txt', filemode='a', format='%(asctime)s - %(levelname)s - %(message)s')



class Query():


    def send_to_misp(response):
        try:
            with open('/tmp/tmpfile.json', 'w') as f:
                json.dump(response , f)
            misp.upload_stix(path= '/tmp/tmpfile.json')
        except Exception as e:
            logging.error(e)

    def query_paginated(url: str, xheaders):
        while url:
            response = requests.get(url, headers = xheaders)
            Query.send_to_misp(response.json())
            if not response.links or response.status_code == 204:
                logging.info(f'Server Returned: {response.status_code}')
                break
            url = response.links["next"]["url"]

    def fireeye_query(epoch, api_url, limit):
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
        if r.status_code == 204:
                logging.info('Query Complete')
        if r.status_code != 200:
                logging.info(f'Server returned: {r.status_code}')
        if r.status_code == 200:
                Query.send_to_misp(r.json())
                api_url = r.links['next']['url']
                Query.query_paginated(api_url, xheaders)
                


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

     def epoch_fetch(query_days) -> str:
        d = datetime.now()
        p = str((d - timedelta(days=query_days)).timestamp())
        return p



def main():
    parser = argparse.ArgumentParser(description="FireEye API to MISP Events")
    parser.add_argument("query", type=int, help="Number of days to query", default="0")
    args = parser.parse_args()
    query_days = DataManager.epoch_fetch(args.query)
    logging.info(f'Fetching all data since {query_days}')
    try:
        exp = DataManager.token()
    except:
        logging.error(f'{query_days}: Unable to fetch token, please confirm required variables are placed in your .env file')
        sys.exit(0)
    endpoints = [ 'Re', 'Al', 'In']
    length = 0
    try:
        for endpoint in endpoints:
            if endpoint == 'Re':
                print('Getting Reports')
                url = 'https://api.intelligence.fireeye.com/collections/reports/objects'
                length = 100
                Query.indicator_query(query_days, url, length)
            if endpoint == 'Al':
                url = 'https://api.intelligence.fireeye.com/collections/alerts/objects'
                length = 100
                Query.indicator_query(query_days, url, length)
            if endpoint == 'In':
                url = 'https://api.intelligence.fireeye.com/collections/indicators/objects'
                length = 1000
                Query.indicator_query(query_days, url, length)    
    except Exception as e:
        logging.error(e)


main()
