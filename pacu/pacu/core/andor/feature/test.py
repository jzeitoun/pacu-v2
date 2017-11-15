from pacu.util.path import Path
import ujson as json

raw_json = Path.here('all.json').read()
features = json.loads(raw_json)
