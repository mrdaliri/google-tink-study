# NOTE: This script does not support pagination. It is not required now since total
import os
from datetime import datetime

import requests
import csv
from dotenv import load_dotenv

load_dotenv()
github_access_token = os.getenv("ACCESS_TOKEN")

query = '"com.google.crypto.tink" filename:pom.xml filename:build.gradle'

headers = {'Authorization': 'token %s' % github_access_token}

results = []
request_url = 'https://api.github.com/search/code'
request_params = {'q': query}
while True:
    search = requests.get(request_url, params=request_params, headers=headers)
    response = search.json()
    if 'items' not in response:
        break

    results = results + response['items']
    if 'next' in search.links:
        request_url = search.links['next']['url']
        request_params = {}  # unset request params since they are included in the related url
    else:
        break


csv_fields = ['file_name', 'path', 'repo_name', 'repo_url', 'owner', 'owner_type']
saved_records = 0
with open('output_files/github_results_api.csv', 'w', newline='') as output:
    writer = csv.DictWriter(output, fieldnames=csv_fields)
    writer.writeheader()

    for r in results:
        writer.writerow({
            'file_name': r['name'],
            'path': r['path'],
            'repo_name': r['repository']['full_name'],
            'repo_url': r['repository']['html_url'],
            'owner': r['repository']['owner']['login'],
            'owner_type': r['repository']['owner']['type']
        })
        saved_records += 1

print("Saved %d search results." % (saved_records, ))
