import json
import csv
import os
import sys
from datetime import datetime


def generate_csv_files(json_file_path, template_dir, output_dir):
    try:
        # Load JSON data
        with open(json_file_path, 'r') as json_file:
            data = json.load(json_file)
    except FileNotFoundError:
        print(f"Error: JSON file '{json_file_path}' not found.")
        sys.exit(1)
    except json.JSONDecodeError:
        print(f"Error: Invalid JSON format in file '{json_file_path}'.")
        sys.exit(1)

    # Process each object in the JSON data
    for item in data:
        template_file = item['file_template']
        template_path = os.path.join(template_dir, template_file)

        try:
            # Read the template CSV file
            with open(template_path, 'r', newline='') as template_csv:
                reader = csv.reader(template_csv)
                csv_data = list(reader)
        except FileNotFoundError:
            print(f"Error: Template CSV file '{template_path}' not found.")
            continue  # Skip this item and continue with the next

        # Update the third line (index 2) with new values
        csv_data[2] = [
            'TRUE',
            item['labcode'],
            item['batch'],
            item['sample_name'],
            item['acquisition_date'],
            item['acquisition_time'],
            item['operator'],
            item['instrument'],
            '',
            ''
        ]

        # Create output directory if it doesn't exist
        batch_output_dir = os.path.join(output_dir, item['batch'])
        os.makedirs(batch_output_dir, exist_ok=True)

        # Generate the new filename
        today = datetime.now().strftime('%Y%m%d')
        new_filename = f"StarLIMSV11{item['cupno']}_{today}_{item['labcode']}_{item['sample_name']}.csv"
        output_path = os.path.join(batch_output_dir, new_filename)

        try:
            # Write the updated data to the new CSV file
            with open(output_path, 'w', newline='') as new_csv:
                writer = csv.writer(new_csv)
                writer.writerows(csv_data)
            print(f"Generated: {output_path}")
        except IOError as e:
            print(f"Error writing file '{output_path}': {e}")


def display_help(script_name):
    print(f"Usage:")
    print(f"  python {script_name} <json_file_path> <template_directory>")
    print(f"  python {script_name} --help")
    print(f"  python {script_name} -h")
    print(f"  python {script_name} --generate-template [filename]")
    print(f"  python {script_name} -g [filename]")
    print("\nOptions:")
    print("  <json_file_path>        Path to the JSON file containing the data for CSV generation")
    print("  <template_directory>    Directory containing the template CSV files")
    print("  --help, -h              Display this help message")
    print("  --generate-template, -g Generate a template JSON file")
    print("  [filename]              Optional: Specify a name for the generated template file (default: template.json)")


def generate_json_template(filename='template.json'):
    template = [{
        "file_template": "example_template.csv",
        "cupno": "000",
        "labcode": "0000",
        "batch": "0000T00000B",
        "sample_name": "00000000000",
        "acquisition_date": "MM/DD/YY",
        "acquisition_time": "HH:MM:SS",
        "operator": "OPERATOR_NAME",
        "instrument": "INSTRUMENT_NAME"
    }]

    # Ensure the filename has a .json extension
    if not filename.lower().endswith('.json'):
        filename += '.json'

    try:
        with open(filename, 'w') as json_file:
            json.dump(template, json_file, indent=2)
        print(f"JSON template generated: {filename}")
    except IOError as e:
        print(f"Error creating template file '{filename}': {e}")
        sys.exit(1)


if __name__ == "__main__":
    script_name = os.path.basename(sys.argv[0])

    if len(sys.argv) == 1 or sys.argv[1] in ['--help', '-h']:
        display_help(script_name)
    elif sys.argv[1] in ['--generate-template', '-g']:
        if len(sys.argv) == 3:
            generate_json_template(sys.argv[2])
        else:
            generate_json_template()
    elif len(sys.argv) == 3:
        json_file_path = sys.argv[1]
        template_dir = sys.argv[2]
        output_dir = "output"  # You can change this to your preferred output directory
        generate_csv_files(json_file_path, template_dir, output_dir)
    else:
        print("Error: Invalid number of arguments.")
        print(
            f"Use 'python {script_name} --help' or 'python {script_name} -h' for usage information.")
        sys.exit(1)
