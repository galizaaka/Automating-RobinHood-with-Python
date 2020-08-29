import json
def serialize_it(orders):
    d = json.dumps(orders)
    return json.loads(d)