import configparser

CONFIG_FILE = "config.txt"

def load_config():
    config = configparser.ConfigParser()
    config.read(CONFIG_FILE, encoding="utf-8")

    if "DEFAULT" not in config:
        return {}

    return dict(config["DEFAULT"])

def save_config(values: dict):
    config = configparser.ConfigParser()
    config["DEFAULT"] = values
    with open(CONFIG_FILE, "w", encoding="utf-8") as f:
        config.write(f)
