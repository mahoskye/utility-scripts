#################################################
# Outputs filenames and sample name from CSV files
#
# For when sample names are stored in csv files at
# a specific row/column and you need to compare it
# to the file name.
#################################################

import os
import csv

# Specify the directory path
directory_path = r'C:\Users'

# Get a list of filenames in the directory
filenames = os.listdir(directory_path)

sample_info = []

# Print the filenames
for filename in filenames:
    filename_sample_info = filename.split(
        "_")[3].replace(".csv", "").replace("-1", "")
    with open(os.path.join(directory_path, filename), 'r') as csvfile:
        reader = csv.reader(csvfile)
        data = list(reader)

        if len(data) > 2:
            if len(data[2]) > 3:
                file_sample_info = data[2][3]

    sample_info.append((filename_sample_info, file_sample_info))


print(sample_info)
