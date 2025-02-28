import datetime
import json


def get_config():
    with open("config.json", "r", encoding='utf-8') as f:
        text = json.loads(f.read())
        text["order_time"] = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        return text
