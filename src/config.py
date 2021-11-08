import json

def load(filename):
	raw_json = open(f"../config/{filename}.json")
	json_data = json.load(raw_json)
	return json_data

def update(target, new_config, filename="colors"):
	config = load(filename)
	config[target] = new_config

	with open('../config/colors.json', 'w') as fhand:
		json.dump(config, fhand, indent=2)


