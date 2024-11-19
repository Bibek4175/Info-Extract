import json

file_path = '/content/cdx-00000'

structured_data = []

with open(file_path, 'r') as file:
    for i, line in enumerate(file):
        if i >= 500:
            break

        parts = line.split(' ', 1)
        if len(parts) < 2:
            continue

        url= parts[0].strip(')/')
        url_key = url.split(')')[0]
        timestamp, json_data = parts[1].split(' ', 1)

        try:
            json_entry = json.loads(json_data)
        except json.JSONDecodeError:
            print(f"Error decoding JSON for line: {line.strip()}")
            continue

        structured_entry = {
            "urlkey": url_key,
            "timestamp": timestamp,
            **json_entry
        }


        structured_data.append(structured_entry)

# Output the structured data
for item in structured_data:
    print(json.dumps(item, indent=2))  # Pretty-print each JSON entry

