import json


def write_to_json_file(path: str, data: dict) -> None:
    """
    Write a string to a JSON file.

    Parameters:
    file_path (str): The path of the JSON file.
    data (str): The dictionary to convert to the JSON file.

    Returns:
    None
    """
    with open(path, 'w') as json_file:
        json.dump(data, json_file)

def dump_output(modelID : str, output, path : str = None) -> None:
	"""
	Write a string to a JSON file.

	Parameters:
	file_path (str): The path of the JSON file.
	data (str): The dictionary to convert to the JSON file.

	Returns:
	None
	"""
	if path is None:
		write_to_json_file("output.json", {"modelID":modelID,"output":output})
	else:
		write_to_json_file(path, {"modelID":modelID,"output":output})

def retrieve_output(path : str, output : str = None) -> None:
	"""
	Retrieve output from JSON file.

	Parameters:
	path (str): The path of the JSON file.
	output (str): The output field name to be retrieved.

	Returns:
	None
	"""
	if output is None:
		output = "output"
	with open(path, 'r') as json_file:
		data = json.load(json_file) #generate dictionary from json
		return data[output]


if __name__ == "__main__":
    try:
        dump_output("CC", 1, "output.json")
        print(retrieve_output(path="output.json"))
    except:
        pass