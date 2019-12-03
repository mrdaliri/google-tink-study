import subprocess
import os
import csv
from pathlib import Path

from dotenv import load_dotenv

load_dotenv(override=True)
git_root = 'repositories'
# git_root = 'sample_repos'
test_reports = 'test_reports'
# repos_csv = 'output_files/build_report_github_results_sample.csv'
repos_csv = 'output_files/build_report_github_results_01122019_1242.csv'
analyzer_reports = 'analyser_reports'
processes = dict()
max_processes = 5

crypto_directory = 'crypto_analysis'
rules_directory = os.path.join(crypto_directory, 'rules')
analyzer_jar_file = os.path.join(crypto_directory, 'CryptoAnalysis-2.6.1.jar')
csv_report = open('output_files/test_report_%s' % Path(repos_csv).name, 'w')
report_writer = csv.DictWriter(csv_report, fieldnames=['file_name', 'repo_name', 'file_path', 'file_url', 'commit_sha',
                                                       'p_language', 'process_status'])
report_writer.writeheader()


def encode(record):
    return '%(repo)s__%(sha)s' % {'repo': record['repo_name'].replace('/', '_'), 'sha': record['commit_sha']}


def save_result(p):
    record = p[0]
    process_status = p[1].poll()

    del record['actual_status']
    record['process_status'] = process_status
    report_writer.writerow(record)
    print("Process finished with status P%s for %s" % (process_status, record['file_url']))


def analyze():
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

            reports_folder = os.path.join(test_reports, encoded_name)
            if not os.path.exists(reports_folder):
                os.mkdir(reports_folder)
            build_output = open(os.path.join(reports_folder, '%s_output.txt' % record['file_path'].replace('/', '_')),
                                'w+')
            build_error = open(os.path.join(reports_folder, '%s_error.txt' % record['file_path'].replace('/', '_')),
                               'w+')

            classes_path = ''
            if record['file_name'] == 'pom.xml':
                classes_path = os.path.join(build_parent_path, 'target', 'classes')
            else:
                classes_path = os.path.join(build_parent_path, 'build', 'classes')

            analysis_folder = os.path.join(analyzer_reports, encoded_name)
            if not os.path.exists(analysis_folder):
                os.mkdir(analysis_folder)
            analyzer_report = os.path.join(analysis_folder, record['file_path'].replace('/', '_').replace('.', '_'))
            if not os.path.exists(analyzer_report):
                os.mkdir(analyzer_report)
            report_csv_file = os.path.join(analysis_folder, 'report_%s.csv' % record['file_path'].replace('/', '_'))

            command = 'java -cp %(crypto_jar)s crypto.HeadlessCryptoScanner --rulesDir=%(rules)s --applicationCp=%(app)s --reportDir=%(report_dir)s --csvReportFile=%(csv_file)s --softwareIdentifier=%(id)s' % {'rules': os.path.abspath(rules_directory), 'crypto_jar': os.path.abspath(analyzer_jar_file), 'app': os.path.abspath(classes_path), 'report_dir': os.path.abspath(analyzer_report), 'csv_file': os.path.abspath(report_csv_file), 'id': record['file_path']}
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


analyze()
