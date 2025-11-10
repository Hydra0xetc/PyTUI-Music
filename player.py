import os
import curses
import time
import sys
import mpv
import subprocess
from datetime import datetime
from wcwidth import wcswidth
from utils import truncate_string_to_width, get_scrolling_display_string
from config import save_config, load_seen_songs, save_seen_songs
from tui import draw_message_box

supported_exts = ('.mp3', '.wav', '.flac', '.m4a', '.ogg')

def draw_player_tui(
        stdscr,
        player,
        playlist,
        selected_idx,
        playing_idx,
        playlist_view_offset,
        now_playing_text_scroll_offset,
        selected_song_text_scroll_offset,
        song_lock,
        config,
        new_songs_indices
):

    h, w = stdscr.getmaxyx()
    max_width = w - 4

    stdscr.erase()
    stdscr.box()

    # Now Playing section
    if player.playlist_pos is not None and 0 <= player.playlist_pos < len(playlist):
        title = player.media_title or os.path.basename(playlist[player.playlist_pos])
    else:
        title = "Nothing playing"
    display_title = get_scrolling_display_string(title, max_width, now_playing_text_scroll_offset)
    stdscr.addstr(1, 2, "Now Playing:", curses.A_BOLD)
    stdscr.addstr(2, 2, display_title)

    # Progress bar
    pos = player.playback_time or 0
    dur = player.duration or 0
    time_str_base = f"{time.strftime('%M:%S',
                       time.gmtime(pos))} / {time.strftime('%M:%S',
                       time.gmtime(dur))}"

    bar_length_calc = min(30, w - wcswidth(time_str_base) - 10) 
    bar_str = ""
    if dur > 0 and bar_length_calc > 5:
        progress = (pos / dur)
        filled_length = int(bar_length_calc * progress)
        bar_str = '█' * filled_length + '.' * (bar_length_calc - filled_length)

    full_time_str = f"{time_str_base} [{bar_str}];" if bar_str else time_str_base
    
    # Truncate full_time_str before adding to screen
    truncated_full_time_str = truncate_string_to_width(full_time_str, w - 4) # w - 4 for padding
    stdscr.addstr(3, 2, truncated_full_time_str)

    if player.pause:
        paused_text = "[PAUSED]"
        paused_x = w - wcswidth(paused_text) - 2 
        if paused_x < 2:
            paused_x = 2 # Ensure it doesn't go off screen to the left
        stdscr.addstr(1, paused_x, paused_text, curses.A_REVERSE)

    if song_lock:
        lock_text = "[LOCKED]"
        lock_x = w - wcswidth(lock_text) - 2
        if lock_x < 2:
            lock_x = 2
        stdscr.addstr(2, lock_x, lock_text, curses.A_REVERSE)

    stdscr.hline(4, 1, curses.ACS_HLINE, w - 2)

    # Playlist display
    playlist_h = h - 7
    start_line = 5



    for i in range(playlist_h):
        song_idx = i + playlist_view_offset
        if song_idx < len(playlist):
            song_name = os.path.basename(playlist[song_idx])
            
            indicator_char = "*" if song_idx in new_songs_indices else " "
            selection_char = "> " if song_idx == playing_idx else " "
            
            prefix = f"{indicator_char}{selection_char} " 
            
            item_number = f"{song_idx + 1}."

            max_song_width = max_width - len(prefix) - len(item_number) - 1
            if song_idx == selected_idx:
                display_text = get_scrolling_display_string(
                    song_name,
                    max_song_width,
                    selected_song_text_scroll_offset
                )

                stdscr.addstr(
                    start_line + i,
                    2,
                    f"{prefix}{item_number} {display_text}",
                    curses.A_REVERSE
                )

            else:
                display_text = truncate_string_to_width(
                    song_name,
                    max_song_width
                )

                stdscr.addstr(
                    start_line + i,
                    2,
                    f"{prefix}{item_number} {display_text}"
                )

    # Footer
    vol = player.volume
    help1 = f"Volume: {vol:.0f}% (9/0)"
    cava_help = " | C : cava" if config.get('cava', False) else ""
    help2 = f"↑/↓: Select | Enter: Play | p: Pause | l: Lock | b/n: Prev/Next{cava_help} | q: Exit"

    # Truncate help texts to fit within screen width
    max_footer_width = w - 4 # 2 chars padding on each side
    truncated_help1 = truncate_string_to_width(help1, max_footer_width)
    truncated_help2 = truncate_string_to_width(help2, max_footer_width)

    stdscr.addstr(h - 2, 2, truncated_help1)
    stdscr.addstr(h - 2, w - wcswidth(truncated_help2) - 2, truncated_help2)
    stdscr.noutrefresh()

def player_tui(
        stdscr,
        folder_path, 
        initial_volume, 
        config
):

    curses.curs_set(0)
    stdscr.timeout(100)  # Faster response

    playlist = sorted([
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(supported_exts)
    ])

    if not playlist:
        draw_message_box(stdscr, "No audio files found in this folder.")
        return

    seen_songs_data = load_seen_songs()
    new_songs_indices = []
    now = datetime.now()

    # Check if the folder path is a key in our data.
    if folder_path not in seen_songs_data:
        # This is a new folder.
        # 1. Don't show any asterisks for this run.
        new_songs_indices = []
        
        # 2. Create a new dictionary for this folder's songs.
        new_folder_data = {}
        for song_full_path in playlist:
            filename = os.path.basename(song_full_path)
            new_folder_data[filename] = now.isoformat()
            
        # 3. Add this new folder's data to the main structure.
        seen_songs_data[folder_path] = new_folder_data
    else:
        # This is an existing folder. Check for new songs.
        current_folder_data = seen_songs_data[folder_path]
        for i, song_full_path in enumerate(playlist):
            filename = os.path.basename(song_full_path)
            if filename not in current_folder_data:
                # It's a new song in an old folder. Mark it as new.
                new_songs_indices.append(i)
                # Add the new song to the data for saving.
                current_folder_data[filename] = now.isoformat()

    try:
        player = mpv.MPV(
            video=False,
            input_default_bindings=False,
            input_vo_keyboard=False,
            osc=False,
            audio_device=config.get('audio_backend', 'auto'),
            vo='null'
        )
            
        player.volume = initial_volume
        player.loop_playlist = 'inf' # Loop the playlist indefinitely

        for f in playlist:
            player.playlist_append(f)

        player.playlist_pos = 0
        player.pause = False
        selected_idx = 0
        playlist_view_offset = 0
        now_playing_text_scroll_offset = 0
        selected_song_text_scroll_offset = 0
        now_playing_scroll_counter = 0
        current_playing_id = None
        last_selected_idx = -1
        song_lock = False

        while True:
            try:
                # Adjust playlist_view_offset (scrolling logic)
                h, w = stdscr.getmaxyx()
                playlist_h = h - 7
                if selected_idx >= playlist_h + playlist_view_offset:
                    playlist_view_offset = selected_idx - playlist_h + 1
                elif selected_idx < playlist_view_offset:
                    playlist_view_offset = selected_idx

                playing_idx = player.playlist_pos \
                if player.playlist_pos is not None else -1

                if playing_idx != current_playing_id:
                    current_playing_id = playing_idx
                    now_playing_text_scroll_offset = 0
                    now_playing_scroll_counter = 0

                if selected_idx != last_selected_idx:
                    selected_song_text_scroll_offset = 0
                    last_selected_idx = selected_idx

                draw_player_tui(
                    stdscr,
                    player,
                    playlist,
                    selected_idx,
                    playing_idx,
                    playlist_view_offset,
                    now_playing_text_scroll_offset,
                    selected_song_text_scroll_offset,
                    song_lock, 
                    config,
                    new_songs_indices
                )

                now_playing_scroll_counter += 1
                if now_playing_scroll_counter >= 3:  # Scroll faster
                    now_playing_text_scroll_offset += 1
                    selected_song_text_scroll_offset += 1
                    now_playing_scroll_counter = 0

                curses.doupdate()

            except Exception as e:
                sys.stderr.write(f"Error in player loop: {e}\n")
                sys.stderr.flush()
                continue

            key = stdscr.getch()

            if key == -1:
                continue

            if key == ord('C'):
                exe = config.get('background')
                if exe:
                    curses.endwin()
                    try:
                        subprocess.run([exe])
                    except FileNotFoundError:
                        stdscr.clear()
                        draw_message_box(
                            stdscr,
                            f"'{exe}' command not found. Please install it."
                        )

                    except Exception as e:
                        stdscr.clear()
                        draw_message_box(
                            stdscr,
                            f"Error running {exe}: {e}"
                        )

                    stdscr.refresh()
                    continue
            elif key == curses.KEY_UP:
                selected_idx = max(0, selected_idx - 1)

            elif key == curses.KEY_DOWN:
                selected_idx = min(len(playlist) - 1, selected_idx + 1)

            elif key == curses.KEY_ENTER or key in [10, 13]:
                player.playlist_pos = selected_idx
                player.pause = False

            elif key == ord('p'):
                player.pause = not player.pause

            elif key == ord('l'):
                song_lock = not song_lock
                player.loop_file = 'inf' if song_lock else False

            elif key == ord('b'):
                if len(playlist) > 0:
                    if player.playlist_pos == 0:
                        player.playlist_pos = len(playlist) - 1
                    else:
                        player.playlist_prev()

            elif key == ord('n'):
                if len(playlist) > 0:
                    if player.playlist_pos == len(playlist) - 1:
                        player.playlist_pos = 0
                    else:
                        player.playlist_next()

            elif key == ord('9'):
                player.volume = max(0, player.volume - 2)
                config['volume'] = player.volume
                save_config(config)

            elif key == ord('0'):
                player.volume = min(150, player.volume + 2)
                config['volume'] = player.volume
                save_config(config)

            elif key == ord('q'):
                save_seen_songs(seen_songs_data)
                player.quit()
                break

    except Exception as e:
        draw_message_box(stdscr, f"An error occurred: {e}")
        curses.endwin()
