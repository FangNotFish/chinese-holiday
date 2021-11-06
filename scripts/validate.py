import pathlib
import datetime
import json
import jsonschema
import glob

BASE_DIR = pathlib.Path(__file__).parent.parent / "dataset"


def _load_json(fn):
    with open(fn, "r", encoding="utf-8") as fp:
        return json.load(fp)


SCHEMA = _load_json(BASE_DIR / ".schema")


class Validator:
    def __init__(self):
        self.year_list = []

    def __call__(self, fn):
        instance = _load_json(fn)
        jsonschema.validate(instance=instance, schema=SCHEMA)

        self._validate(**instance)

    def _validate(self, *, Year, Source, Contributors, Content):
        if Year in self.year_list:
            raise ValueError(f"Year MUST be unique: {Year}")
        self.year_list.append(Year)

        reason_list = []
        for item in Content:
            reason = item["Reason"]

            if reason in reason_list:
                raise ValueError(f"Reason MUST be unique: {reason}")
            reason_list.append(reason)

            holiday_list = []
            for holiday in item["Holiday"]:
                if holiday in holiday_list:
                    raise ValueError(f"Holiday MUST be unique: {holiday}")
                holiday_list.append(holiday)

            special_workday_list = []
            for special_workday in item["SpecialWorkday"]:
                if special_workday in special_workday_list:
                    raise ValueError(
                        f"SpecialWorkday MUST be unique: {special_workday}"
                    )
                special_workday_list.append(special_workday)

                date = datetime.datetime.strptime(
                    special_workday, r"%Y/%m/%d"
                ).date()

                if date.weekday() not in (5, 6):
                    raise ValueError(
                        f"WTF: weekday 1-5 is workday"
                    )


def validate(files=None, no_raise=True):
    files = files or glob.glob(str(BASE_DIR / "*.json"))

    validator = Validator()

    for fn in files:
        try:
            validator(fn)
        except BaseException as e:
            if not no_raise:
                raise
            yield fn, e
        else:
            if no_raise:
                yield fn, None


if __name__ == '__main__':
    validate(no_raise=False)
