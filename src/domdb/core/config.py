import os
import tomllib

DEFAULT_CONFIG = {
    "cases_directory": "~/domdatabasen/cases",
    "bib_output": "resources/cases.bib",
    "batch_size": 25,
}

CONFIG_PATH = os.path.expanduser("~/.domdb/config.toml")


def load_config():
    """Load configuration from file or use defaults."""
    config = DEFAULT_CONFIG.copy()
    if os.path.exists(CONFIG_PATH):
        with open(CONFIG_PATH, "rb") as f:
            user_config = tomllib.load(f)
        config.update(user_config)
    config["cases_directory"] = os.path.expanduser(config["cases_directory"])
    return config
