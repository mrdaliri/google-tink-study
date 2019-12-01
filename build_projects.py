import subprocess
import os
import csv
from pathlib import Path
from dotenv import load_dotenv

load_dotenv()
git_root = 'repositories'
build_reports = 'build_reports'
repos_csv = 'github_results_01122019_1242.csv'
processes = dict()
max_processes = 1

csv_report = open('build_report_%s' % repos_csv, 'w')
report_writer = csv.DictWriter(csv_report, fieldnames=['file_name', 'file_url', 'actual_status', 'process_status'])


def encode(record):
    return '%(repo)s__%(sha)s' % {'repo': record['repo_name'].replace('/', '_'), 'sha': record['commit_sha']}


def save_result(p):
    record = p[0]
    err = p[1].stderr.read()
    out = p[1].stdout.read()
    process_status = p[1].poll()

    reports_folder = os.path.join(build_reports, encode(record))
    if not os.path.exists(reports_folder):
        os.mkdir(reports_folder)
    build_output = open(os.path.join(reports_folder, '%s_output.txt' % record['file_path'].replace('/', '_')), 'wb')
    build_error = open(os.path.join(reports_folder, '%s_error.txt' % record['file_path'].replace('/', '_')), 'wb')
    build_output.write(out)
    build_output.close()
    build_error.write(err)
    build_error.close()

    actual_result = int(str(err).upper().find('BUILD FAIL') != -1 or str(out).upper().find('BUILD FAIL') != -1)
    report_writer.writerow(
        {'actual_status': actual_result, 'process_status': process_status, 'file_url': record['file_url'],
         'file_name': record['file_name']})
    print("Process finished with status P%s-A%s for %s" % (process_status, actual_result, record['file_url']))


def proc():
    with open(repos_csv, newline='') as csv_file:
        reader = csv.DictReader(csv_file)

        for record in reader:
            encoded_name = encode(record)
            main_folder = os.path.join(git_root, encoded_name)
            build_file_path = os.path.join(main_folder, record['file_path'])
            build_parent_path = Path(build_file_path).parent

            command = ''
            if record['file_name'] == 'pom.xml':
                command = 'mvn compile'
            else:
                command = 'gradle wrapper'
            processes[record['file_path']] = [record,
                                              subprocess.Popen(command.split(' '),
                                                               cwd=build_parent_path,
                                                               stdout=subprocess.PIPE,
                                                               stderr=subprocess.PIPE)]
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
        else:
            save_result(processes[i])
            del processes[i]


proc()