#!/bin/bash

# Loop through all Python files in the current directory
for file in *.py; do
    # Extract filename without extension
    name="${file%.py}"

    # Run tf_upgrade_v2 command
    tf_upgrade_v2 --infile "$file" --reportfile "report_${name}.txt" --inplace
done