import json
import csv
json_in_path = ''
csv_dump_path = ''

with open(json_dump_path, 'r', encoding='utf8', errors='ignore') as f:
    data = json.load(f)
    list_of_data = data['data']
    parsed_strings = [message['string'] for message in list_of_data]
    unique_strings = list(set(parsed_strings))
    with open(csv_dump_path, 'w', encoding="utf-8",newline='') as result_file:
        wr = csv.writer(result_file, delimiter=',', quotechar='"')
        for string in unique_strings:
            if len(string) > 3:
                wr.writerow([string])