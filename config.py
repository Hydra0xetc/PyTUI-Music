import os
import json

CONFIG_FILE = os.path.expanduser("~/.configure.json")  # Consolidated config file

def load_config():
    """Loads the configuration from the config file."""
    default_config = {'paths': [], 'volume': 50}
    try:
        if os.path.exists(CONFIG_FILE):
            with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Validate and clean paths
                config['paths'] = sorted(list(set([p for p in config.get('paths', []) if os.path.isdir(p)])))
                # Validate volume
                config['volume'] = max(0, min(100, int(config.get('volume', 50))))
                return config
    except (json.JSONDecodeError, FileNotFoundError):
        pass
    return default_config

def save_config(config):
    """Saves the configuration to the config file."""
    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config, f, indent=4)
    except IOError:
        pass
