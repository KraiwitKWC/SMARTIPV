import csv
import json

def convert_csv_to_json(csv_content):
    # Split the content into lines
    lines = csv_content.strip().split('\n')

    # Ensure there are enough lines for metadata and data
    if len(lines) < 7:
        raise ValueError("The CSV content does not have enough lines for metadata and data.")

    # Read metadata
    metadata = {
        "CPUID": lines[0].split(':')[1].strip(),
        "Processor": lines[1].split(':')[1].strip(),
        "Platform": lines[2].split(':')[1].strip(),
        "Revision": lines[3].split(':')[1].strip(),
        "Lithography": lines[4].split(':')[1].strip(),
        "Session start": lines[5].split(':', 1)[1].strip()
    }

    # Read CSV headers and rows
    csv_data = '\n'.join(lines[7:])
    
    # Create a CSV reader object
    csv_reader = csv.DictReader(csv_data.splitlines())
    
    # Convert CSV rows to JSON format
    data_list = [row for row in csv_reader]
    
    # Combine metadata and data
    result = {
        "metadata": metadata,
        "data": data_list
    }
    
    return json.dumps(result, indent=4)

# Read CSV content from file
file_path = r'C:\Program Files\Core Temp\CT-Log 2024-09-10 13-41-27.csv'
with open(file_path, 'r') as file:
    csv_content = file.read()

# Convert and print the JSON data
json_output = convert_csv_to_json(csv_content)
print(json_output)
