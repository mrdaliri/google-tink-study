import subprocess
import os
import csv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)
git_root = 'repositories'
# git_root = 'sample_repos'
build_reports = 'build_reports'
repos_csv = 'output_files/github_results_01122019_1242.csv'
# repos_csv = 'output_files/github_results_sample.csv'
processes = dict()
max_processes = 5

csv_report = open('output_files/build_report_%s' % Path(repos_csv).name, 'w')
report_writer = csv.DictWriter(csv_report, fieldnames=['file_name', 'repo_name', 'file_path', 'file_url', 'commit_sha',
                                                       'p_language', 'actual_status', 'process_status'])
report_writer.writeheader()


def encode(record):
    return '%(repo)s__%(sha)s' % {'repo': record['repo_name'].replace('/', '_'), 'sha': record['commit_sha']}


def save_result(p):
    record = p[0]
    process_status = p[1].poll()

    reports_folder = os.path.join(build_reports, encode(record))
    if not os.path.exists(reports_folder):
        os.mkdir(reports_folder)
    build_output = open(os.path.join(reports_folder, '%s_output.txt' % record['file_path'].replace('/', '_')), 'r')
    build_error = open(os.path.join(reports_folder, '%s_error.txt' % record['file_path'].replace('/', '_')), 'r')

    err = build_error.read()
    out = build_output.read()

    actual_result = int(str(err).upper().find('BUILD FAIL') != -1 or str(out).upper().find('BUILD FAIL') != -1)
    report_writer.writerow(record.update({'actual_status': actual_result, 'process_status': process_status}))
    print("Process finished with status P%s-A%s for %s" % (process_status, actual_result, record['file_url']))


def proc():
    with open(repos_csv, newline='') as csv_file:
        reader = csv.DictReader(csv_file)

        for record in reader:
            encoded_name = encode(record)
            main_folder = os.path.join(git_root, encoded_name)
            build_file_path = os.path.join(main_folder, record['file_path'])
            build_parent_path = Path(build_file_path).parent

            reports_folder = os.path.join(build_reports, encode(record))
            if not os.path.exists(reports_folder):
                os.mkdir(reports_folder)
            build_output = open(os.path.join(reports_folder, '%s_output.txt' % record['file_path'].replace('/', '_')),
                                'w+')
            build_error = open(os.path.join(reports_folder, '%s_error.txt' % record['file_path'].replace('/', '_')),
                               'w+')

            command = ''
            if record['file_name'] == 'pom.xml':
                command = 'mvn clean compile'
            else:
                command = './gradlew clean build'
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


proc()
