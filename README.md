# PyTUI_Music

**Important Warning: This program is in a very early stage of development and has many limitations and potential bugs. The user experience may not be optimal.**

## Features

- **Terminal-Based UI**: A lightweight, keyboard-driven interface that runs in your terminal.
- **File & Directory Browser**: Easily browse your filesystem to add music directories.
- **Playlist Management**: Automatically creates a playlist from the audio files in a selected folder.
- **Playback Control**: Play, pause, skip tracks, and control volume with simple keybindings.
- **Configuration File**: Saves your music paths and volume settings in a `~/.config/PyTUI_Music/config.conf` file.

## Installation

1.  **Clone the repository or download the files.**

2.  **Install the required Python libraries:**

    ```bash
    pip install -r requirements.txt
    ```

    The required libraries are:
    - `wcwidth`

## How to Use

1.  **Run the application:**

    ```bash
    python main.py
    ```

2.  **Adding a Music Path:**
    - **Important:** When adding a music path, you should select a parent directory that contains multiple sub-folders. Each of these sub-folders will be treated as an "album" by the player. For example, if you have a `~/Music` directory, and inside it are folders like `Album A`, `Album B`, etc., you should add `~/Music` as your base path.
    - If this is your first time running the app, you will be prompted to `[ Add New Path ]`.
    - Use the arrow keys (↑/↓) to navigate the file browser.
    - Press `Enter` to enter a directory.
    - Navigate to the directory you want to add as a base music folder.
    - Press `s` or select `[ Select Current Directory ]` and press `Enter` to save the path.

3.  **Selecting a Folder to Play:**
    - After adding a base path, you will see a list of your saved paths.
    - Select a base path and press `Enter`.
    - You will then see a list of sub-folders within that path.
    - Select a folder containing your music files and press `Enter`.

4.  **Controlling the Player:**
    - The player interface will load with the playlist from the selected folder.
    - **↑/↓**: Navigate the playlist.
    - **Enter**: Play the selected song.
    - **p**: Toggle play/pause.
    - **b**: Play the previous song.
    - **n**: Play the next song.
    - **l**: Lock the song.
    - **q**: Quit the player and return to the folder selection menu.
