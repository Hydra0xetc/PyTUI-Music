import os
import json

CONFIG_FILE = os.path.expanduser("~/.configure.json")  # Consolidated config file

def load_config():
    """Loads the configuration from the config file, creating it if it doesn't exist."""
    default_config = {
        'paths': [],
        'volume': 50,
        'audio_backend': 'auto',
        'cava': False
    }

    if not os.path.exists(CONFIG_FILE):
        save_config(default_config)
        return default_config

    try:
        with open(CONFIG_FILE, 'r') as f:
            config = json.load(f)
            # Remove comment if it exists from old configs
            config.pop('_comment', None)
            # Validate and clean paths
            config['paths'] = sorted(list(set([p for p in config.get('paths', []) if os.path.isdir(p)])))
            # Validate volume
            config['volume'] = max(0, min(150, int(config.get('volume', 50))))
            # Ensure other keys are present
            config.setdefault('audio_backend', 'auto')
            config.setdefault('cava', False)
            return config
    except (json.JSONDecodeError, FileNotFoundError):
        # If file is corrupted or unreadable, create a new one
        save_config(default_config)
        return default_config

def save_config(config):
    """Saves the configuration to the config file."""
    config_to_save = config.copy()
    # Remove comment key if it exists before saving
    config_to_save.pop('_comment', None)

    try:
        with open(CONFIG_FILE, 'w') as f:
            json.dump(config_to_save, f, indent=4)
    except IOError:
        pass
