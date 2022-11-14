import os
import json


def search_request_data():
    path_cwd = os.path.dirname(__file__)
    f = open(path_cwd + "/search_request.json")
    return json.load(f)[0]
