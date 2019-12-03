import json
import subprocess
import os
import csv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)
git_root = 'repositories'
# git_root = 'sample_repos'
cloc_reports = 'cloc_reports'
# repos_csv = 'output_files/build_report_github_results_sample.csv'
repos_csv = 'output_files/build_report_github_results_01122019_1242.csv'
processes = dict()
max_processes = 5

all_packages = {}
json_report = open('output_files/cloc_report_%s.json' % Path(repos_csv).name.replace('.csv', ''), 'w')


def encode(record):
    return '%(repo)s__%(sha)s' % {'repo': record['repo_name'].replace('/', '_'), 'sha': record['commit_sha']}


def save_result(p):
    record = p[0]
    process_status = p[1].poll()

    print("Process finished with status P%s for %s" % (process_status, record['file_url']))
    if int(process_status) != 0:
        return

    reports_folder = os.path.join(cloc_reports, encode(record))
    cloc_output = open(os.path.join(reports_folder, '%s_output.txt' % record['file_path'].replace('/', '_')), 'r')
    try:
        result = json.load(cloc_output)
        del result['header']
        all_packages[record['file_url']] = result
    except Exception as ex:
        print("Cannot read cloc's JSON output: %s" % str(ex))


def count():
    with open(repos_csv, newline='') as csv_file:
        reader = csv.DictReader(csv_file)

        for record in reader:
            encoded_name = encode(record)
            main_folder = os.path.join(git_root, encoded_name)
            build_file_path = os.path.join(main_folder, record['file_path'])
            build_parent_path = Path(build_file_path).parent

            if int(record['actual_status']) == 1:
                print("Skip %s due to `actual_status` = 1" % build_parent_path)
                continue

            reports_folder = os.path.join(cloc_reports, encoded_name)
            if not os.path.exists(reports_folder):
                os.mkdir(reports_folder)
            build_output = open(os.path.join(reports_folder, '%s_output.txt' % record['file_path'].replace('/', '_')),
                                'w+')
            build_error = open(os.path.join(reports_folder, '%s_error.txt' % record['file_path'].replace('/', '_')),
                               'w+')

            command = 'cloc %s --include-lang=Java,Scala,Kotlin --json' % os.path.abspath(build_parent_path)
            processes[record['file_url']] = [record,
                                             subprocess.Popen(command.split(' '),
                                                              cwd=build_parent_path,
                                                              stdout=build_output,
                                                              stderr=build_error)]
            print("Running '%s' in %s" % (command, build_parent_path))
            if len(processes) >= max_processes:
                os.wait()

                for i in list(processes.keys()):
                    if processes[i][1].poll() is not None:
                        save_result(processes[i])
                        del processes[i]

    # Check if all the child processes were closed
    for i in list(processes.keys()):
        if processes[i][1].poll() is None:
            processes[i][1].wait()
        save_result(processes[i])

    json.dump(all_packages, json_report)


count()
