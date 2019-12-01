import csv
import requests

git_root = 'repositories'

with open('github_results_01122019_1242.csv', newline='') as csv_file:
    reader = csv.DictReader(csv_file)

    for record in reader:
        download_url = 'https://github.com/%(repo)s/archive/%(sha)s.zip' % {'repo': record['repo_name'],
                                                                            'sha': record['commit_sha']}
        local_file_name = '%(repo)s__%(sha)s.zip' % {'repo': record['repo_name'].replace('/', '_'), 'sha': record['commit_sha']}
        with requests.get(download_url, stream=True) as r:
            r.raise_for_status()
            with open(git_root + '/' + local_file_name, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    if chunk:  # filter out keep-alive new chunks
                        f.write(chunk)

            print("Saved %s as %s." % (str(record), local_file_name))
