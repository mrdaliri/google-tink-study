import os
import sys
from datetime import datetime
from time import sleep
from dotenv import load_dotenv

import requests
import csv
from bs4 import BeautifulSoup


class SearchResult:
    def __init__(self, file_name, repo_name, file_path, file_url, commit_sha, p_language):
        self.file_name = file_name
        self.repo_name = repo_name
        self.file_path = file_path
        self.file_url = file_url
        self.commit_sha = commit_sha
        self.p_language = p_language


def scrap(cookie, query, discard_incomplete_results=True, step_time=10):
    results = []
    user_agent = 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_9_3) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/35.0.1916.47 Safari/537.36'
    headers = {'User-Agent': user_agent, 'Cookie': cookie}
    base_url = 'https://github.com'
    search_url = base_url + '/search'
    request_params = {'q': query, 'type': 'Code'}

    while True:
        search = requests.get(search_url, params=request_params, headers=headers)
        body = search.text
        response = BeautifulSoup(body, 'lxml')
        a = response.select('.d-flex > h3 > span')
        if not a:
            a = response.select('.d-flex > h3')[0]
        else:
            a = a[0]
        print(a.text.strip())
        if discard_incomplete_results is True and body.find('This search took too long to finish') != -1:
            print('Search result is incomplete. Try again in %d seconds.' % step_time, file=sys.stderr)
            sleep(step_time)
            continue

        elements = response.find_all('div', class_='code-list-item')
        print("Result in page: %d" % len(elements))

        for r in elements:
            repo_link = r.select('a.link-gray')[0]
            file_link = r.select('.f4 > a')[0]
            p_language = r.select('span[itemprop=programmingLanguage]')
            if p_language:
                p_language = p_language[0].text
            else:
                p_language = None
            repo_name = repo_link.text.strip()
            file_path = file_link.text.strip()
            file_url = file_link.attrs['href']
            file_name = os.path.basename(file_path)
            commit_sha = file_url  # later should extract commit sha from file direct link

            results.append(SearchResult(file_name, repo_name, file_path, file_url, commit_sha, p_language))

        next_page_link = response.find('a', class_='next_page')
        if not next_page_link:
            break
        else:
            request_params = {}
            search_url = base_url + '/' + next_page_link.attrs['href']

    saved_records = 0
    with open('output_files/github_results.csv', 'w', newline='') as output:
        if len(results) > 0:
            csv_fields = results[0].__dict__

            writer = csv.writer(output)
            writer.writerow(csv_fields)

            for r in results:
                writer.writerow([getattr(r, d) for d in csv_fields])
                saved_records += 1

    print("Saved %d search results." % (saved_records,))


load_dotenv()
cookie = os.getenv("COOKIE")
query = '"com.google.crypto.tink" filename:pom.xml filename:build.gradle'
scrap(cookie=cookie, query=query)
