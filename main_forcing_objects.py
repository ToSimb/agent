import json

agent_scheme = '../agent_scheme.json'

with open(agent_scheme) as json_data:
    data = json.load(json_data)
    print(data)