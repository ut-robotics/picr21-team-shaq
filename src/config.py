import json

def load(filename):
    raw_json = open(f"../config/{filename}.json")
    json_data = json.load(raw_json)
    return json_data

def update(new_config, filename="colors"):
    config = load(filename)
    for key in new_config:
        config[key] = new_config[key]

    with open('../config/colors.json', 'w') as fhand:
        json.dump(config, fhand)


