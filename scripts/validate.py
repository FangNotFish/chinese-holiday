import pathlib
import json
import jsonschema
import glob

BASE_DIR = pathlib.Path(__file__).parent.parent / "dataset"
SCHEMA = BASE_DIR / ".schema"


def _r_open(fn):
    return open(fn, "r", encoding="utf-8")


with _r_open(SCHEMA) as fp:
    schema = json.load(fp)

for fn in glob.glob(str(BASE_DIR / "*.json")):
    with _r_open(fn) as fp:
        try:
            instance = json.load(fp)
        except json.JSONDecodeError:
            # TODO: pretty exception for users
            raise

    try:
        jsonschema.validate(instance=instance, schema=schema)
    except jsonschema.ValidationError as e:
        # TODO: pretty exception for users
        raise
