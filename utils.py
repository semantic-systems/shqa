import json
def load_json_data(file_name):
    try:
        with open(file_name, 'r') as json_file:
            data = json.load(json_file)
        return data['data']
    except FileNotFoundError:
        print(f"Error: File '{file_name}' not found.")
        return []


def write_to_json(result, out_file_path):
    with open(out_file_path, "w", encoding="utf-8") as f:
        json.dump({"data": result}, f, indent=4)

    print("Successfully written to file!")