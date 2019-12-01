#!/bin/bash
repos_folder=$1
extract_repo() {
  zip_file=$1
  output_path=$2;
  unzip -qq "$1" -d "$2_temp";
  created_dir=`find "$2_temp" -maxdepth 1 -mindepth 1 -type d`
  mv -f "$created_dir" "$2" && rm -rf "$2_temp";
}

for f in `find "${repos_folder}" -type f -name "*.zip"`;
  do extract_repo $f "${f/.zip/}";
done
