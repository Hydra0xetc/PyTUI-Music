#!/usr/bin/env python3

import os
import curses
from config import load_config, save_config
from tui import draw_menu, browse_path_tui, draw_message_box
from player import player_tui
from utils import get_folders

def choose_base_path_tui(stdscr, available_paths):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    while True:
        menu_items = []
        if not available_paths:
            menu_items = ["[ Add New Path ]"]  
        else:
            menu_items = available_paths + ["[ Add New Path ]"]

        current_row = 0

        while True:
            draw_menu(
                stdscr,
                current_row, 
                menu_items,
                "Select Music Base Path", 
                "↑/↓: Select | Enter: Open | q: Exit"
            )
            curses.doupdate()
            key = stdscr.getch()

            if key == curses.KEY_UP:
                current_row = (current_row - 1) % len(menu_items)
            elif key == curses.KEY_DOWN:
                current_row = (current_row + 1) % len(menu_items)
            elif key == curses.KEY_ENTER or key in [10, 13]:
                selected_option = menu_items[current_row]
                if selected_option == "[ Add New Path ]":
                    return "__ADD_NEW_PATH__"  
                else:
                    return selected_option  
            elif key == ord('q'):
                return None

def choose_folder_tui(stdscr, base_path):
    curses.curs_set(0)
    curses.init_pair(1, curses.COLOR_BLACK, curses.COLOR_WHITE)

    folders = get_folders(base_path)
    if not folders:
        draw_message_box(stdscr, f"No sub-folders found in {base_path}.")
        return None

    current_row = 0

    while True:
        draw_menu(
            stdscr,
            current_row, 
            folders,
            f"Select Folder in {os.path.basename(base_path)}",
            "↑/↓: Select | Enter: Open | q: Back"
        )

        curses.doupdate()
        key = stdscr.getch()

        if key == curses.KEY_UP:
            current_row = (current_row - 1) % len(folders)
        elif key == curses.KEY_DOWN:
            current_row = (current_row + 1) % len(folders)
        elif key == curses.KEY_ENTER or key in [10, 13]:
            return os.path.join(base_path, folders[current_row])
        elif key == ord('q'):
            return None

def run_app_tui(stdscr):
    while True:
        config = load_config()
        available_base_paths = config['paths']
        selected_base_path = None
        
        chosen_option = choose_base_path_tui(stdscr, available_base_paths)

        if chosen_option == "__ADD_NEW_PATH__":
            new_path = browse_path_tui(stdscr)
            if new_path:
                if os.path.isdir(new_path) and new_path not in config['paths']:
                    config['paths'].append(new_path)
                    config['paths'].sort()
                    save_config(config)
                    draw_message_box(
                        stdscr,
                        f"Path '{new_path}' successfully saved."
                    )
                    
                    selected_base_path = new_path
                else:
                    draw_message_box(
                        stdscr,
                        f"Error: Path '{new_path}' is invalid or already exists."
                    )
                    continue 
            else:
                draw_message_box(stdscr, "Path addition cancelled.")
                continue 

        elif chosen_option is None:
            return

        else:
            selected_base_path = chosen_option
        
        if selected_base_path:
            folder_to_play = choose_folder_tui(stdscr, selected_base_path)
            if folder_to_play:
                player_tui(
                    stdscr,
                    folder_to_play,
                    config['volume'],
                    config
                )
            else: 
                continue
        else:
            continue

def main():

    MIN_H = 10
    MIN_W = 40

    try:
        def start_app(stdscr):
            h, w = stdscr.getmaxyx()
            if h < MIN_H or w < MIN_W:
                
                stdscr.clear()
                stdscr.addstr(
                    0,
                    0,
                    f"Error: Terminal too small. "
                    f"Minimum size required: "
                    f"{MIN_W}x{MIN_H}. Current size: {w}x{h}."
                )
                stdscr.refresh()
                stdscr.getch() 
                return 

            run_app_tui(stdscr)

        curses.wrapper(start_app)
    except curses.error as e:
        print(f"A Curses error occurred: {e}")
        print("Ensure your terminal supports Curses and is large enough.")
    except Exception as e:
        print(f"An unexpected error occurred: {e}")

if __name__ == "__main__":
    main()
