import json
import os
import csv

analyzer_reports = 'analyser_reports'
csv_report = open('output_files/misuses_report.csv', 'w')
merged_report = csv.writer(csv_report)

loc_packages = json.load(open('output_files/cloc_report_build_report_github_results.json', 'r'))
additional_headers = ['count_files', 'count_code_lines']


def encode(record):
    return '%(repo)s__%(sha)s' % {'repo': record['repo_name'].replace('/', '_'), 'sha': record['commit_sha']}


def analyze():
    with open('output_files/test_report_build_report_github_results.csv', newline='') as test_report_file:
        test_report = csv.DictReader(test_report_file)

        header_written = False
        for record in test_report:
            encoded_name = encode(record)

            if int(record['process_status']) == 1:
                print("Skip %s due to `process_status` = 1" % record['file_url'])
                continue

            analysis_folder = os.path.join(analyzer_reports, encoded_name)
            # analyzer_report = os.path.join(analysis_folder, record['file_path'].replace('/', '_').replace('.', '_'))
            report_csv_path = os.path.join(analysis_folder, 'report_%s.csv' % record['file_path'].replace('/', '_'))

            try:
                with open(report_csv_path, newline='') as report_csv_file:
                    report = csv.reader(report_csv_file, delimiter=';')
                    header_row = next(report, None)
                    if not header_written:
                        merged_report.writerow(header_row + additional_headers)
                        header_written = True
                    data = next(report, None)
                    data[0] = record['file_url']
                    try:
                        cloc_record = loc_packages[record['file_url']]
                        data.append(cloc_record['SUM']['nFiles'])
                        data.append(cloc_record['SUM']['code'])
                    except KeyError:
                        data.append(0)
                        data.append(0)
                    merged_report.writerow(data)
            except FileNotFoundError:
                print("Skip %s since its report file is not found." % record['file_url'])


analyze()
