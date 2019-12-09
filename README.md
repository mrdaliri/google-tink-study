# An empirical study on usability of Google Tink cryptographic library

This repository contains all artifacts and scripts as well as results of "An empirical study on usability of Google Tink cryptographic library" research paper (to be published).

## Getting Started

These instructions will get you a copy of the project up and running on your local machine for test and replication purposes.

### Prerequisites

- JDK 8
- Maven
- Gradle
- Python 3.5
- `beautifulsoup4` and `requests` python packages (listed on `requirements.txt`)
- cloc [https://github.com/AlDanial/cloc](https://github.com/AlDanial/cloc)


### Installing

Optionally, create a virtual environment with Python 3.5+ and pip package manager. Then install the required packages:

```
pip3 install -r requirements.txt
```

Copy `sample.env` to `.env` and set the value of `JAVA_HOME` to your JDK installation directory.

## Running the scripts

### New search
To initiate a new search, simply run `github_search_html.py`. This script tries to scrap all possible unique results from GitHub search page.
However, since GitHub search may not return complete result set on each query, it gets lists several times which may take a long time.
The less strict version is available at `github_search_html_duplicates_allowed.py`.

When collection process is done, run `download_repositories.py` to download all source files. Then use `extract_repos.sh` to extract all ZIP files.

Later, run `build_projects.py` to automatically build projects. Results (CSV) and reports are saved in `output_files` and `build_reports` directories, respectively.

Now you can execute `misuse_detector.py` to run CrySL analyzer on built projects. Results (CSV) and reports are saved in `output_files` and `test_reports` folders, respectively.

To count number of lines in each project, simply run `count_lines.py`. Results (JSON) and reports are saved in `output_files` and `cloc_reports` folders, respectively.

Finally, in order to merge all results, run `statistics_merge.py`. Final report is saved in `output_files/misuses_report.csv`.

### Replicate paper results
In order to replicate results presented in paper, first rename `output_files/github_results_01122019_1242.csv` to `output_files/github_results.csv`.

Then download dataset from [https://github.com/mrdaliri/google-tink-dataset](https://github.com/mrdaliri/google-tink-dataset) and extract it in `repositories` folder.

Now you can follow **New search** instructions after the misuse detection section.

## Authors

**Mohammad-Reza Daliri** (daliri@ualberta.ca)

