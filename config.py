import os
import configparser
from pathlib import Path

# Define the path for the configuration file
CONFIG_DIR = Path(os.path.expanduser("~/.config/PyTUI_Music"))
CONFIG_FILE = CONFIG_DIR / "config.conf"

def load_config():
    """Loads the configuration from the config file, creating it if it doesn't exist."""
    if not CONFIG_FILE.is_file():
        # Create default config if it doesn't exist
        default_config_dict = {
            'paths': [],
            'volume': 50,
            'audio_backend': 'auto',
            'cava': True
        }
        save_config(default_config_dict)
        return default_config_dict

    with open(CONFIG_FILE, 'r') as f:
        content = f.read()

    # Manually parse paths
    paths = []
    in_paths_block = False
    config_without_paths = []
    for line in content.splitlines():
        stripped = line.strip()
        if stripped.startswith('paths = ['):
            in_paths_block = True
            if stripped.endswith(']'): # for paths = []
                in_paths_block = False
            continue
        
        if in_paths_block:
            if stripped == ']':
                in_paths_block = False
            else:
                path = stripped.rstrip(',')
                if os.path.isdir(path):
                    paths.append(path)
            continue
        
        config_without_paths.append(line)

    parser = configparser.ConfigParser()
    parser.read_string('\n'.join(config_without_paths))
    
    config = {}
    if 'Settings' in parser:
        settings = parser['Settings']
        config['volume'] = settings.getint('volume', 50)
        config['cava'] = settings.getboolean('cava', True)
        config['audio_backend'] = settings.get('audio_backend', 'auto')

    config['paths'] = paths
    
    # Set defaults and validate
    config.setdefault('volume', 50)
    config.setdefault('cava', True)
    config.setdefault('audio_backend', 'auto')
    config.setdefault('paths', [])
    
    config['paths'] = sorted(list(set(config['paths'])))
    config['volume'] = max(0, min(150, config['volume']))

    return config


def save_config(config_dict):
    """Saves the configuration dictionary to the config file."""
    CONFIG_DIR.mkdir(parents=True, exist_ok=True)
    
    with open(CONFIG_FILE, 'w') as f:
        f.write("# PyTUI_Music Configuration File\n")
        f.write("#\n")
        f.write("# 'paths' is a comma-separated list of directories where your music is stored.\n")
        f.write("# Example: paths = /home/user/Music,/mnt/storage/Music\n")
        f.write("#\n")
        f.write("# 'volume' is the default volume level (0-150).\n")
        f.write("#\n")
        f.write("# 'cava' can be set to True to enable the CAVA audio visualizer (requires CAVA to be installed).\n\n")
        
        f.write("[Settings]\n")
        
        paths = config_dict.get('paths', [])
        if paths:
            f.write("paths = [\n")
            for path in paths:
                f.write(f"  {path},\n")
            f.write("  ]\n\n")
        else:
            f.write("paths = []\n\n")
            
        f.write(f"volume = {int(config_dict.get('volume', 50))}\n")
        f.write(f"audio_backend = {config_dict.get('audio_backend', 'auto')}\n")
        f.write(f"cava = {config_dict.get('cava', True)}\n")
