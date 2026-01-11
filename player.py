import os
import curses
import time
import subprocess
from datetime import datetime
from wcwidth import wcswidth
from utils import truncate_string_to_width, get_scrolling_display_string
from config import save_config, load_seen_songs, save_seen_songs
from tui import draw_message_box

from AndroPlayer import (
    init,
    create_audio_player,
    play,
    pause,
    stop,
    destroy,
    set_looping,
    is_playing,
    cleanup
)

supported_exts = ('.mp3', '.wav', '.flac', '.m4a', '.ogg')

def draw_player_tui(
    stdscr,
    playlist,
    selected_idx,
    playing_idx,
    playlist_view_offset,
    now_playing_scroll,
    selected_scroll,
    song_lock,
    new_songs_indices,
    is_paused
):
    h, w = stdscr.getmaxyx()
    max_width = w - 4

    stdscr.erase()
    stdscr.box()

    # Now Playing
    title = os.path.basename(playlist[playing_idx]) if playing_idx != -1 else "Nothing playing"
    title_disp = get_scrolling_display_string(title, max_width, now_playing_scroll)

    stdscr.addstr(1, 2, "Now Playing:", curses.A_BOLD)
    stdscr.addstr(2, 2, title_disp)

    if is_paused:
        t = "[PAUSED]"
        stdscr.addstr(1, max(2, w - wcswidth(t) - 2), t, curses.A_REVERSE)

    if song_lock:
        t = "[LOCKED]"
        stdscr.addstr(2, max(2, w - wcswidth(t) - 2), t, curses.A_REVERSE)

    stdscr.hline(4, 1, curses.ACS_HLINE, w - 2)

    # Playlist
    playlist_h = h - 7
    start = 5

    for i in range(playlist_h):
        idx = playlist_view_offset + i
        if idx >= len(playlist):
            break

        name = os.path.basename(playlist[idx])
        indicator = "*" if idx in new_songs_indices else " "
        playmark = "> " if idx == playing_idx else "  "
        prefix = f"{indicator}{playmark}"

        num = f"{idx + 1}."
        max_w = max_width - len(prefix) - len(num) - 1

        if idx == selected_idx:
            txt = get_scrolling_display_string(name, max_w, selected_scroll)
            stdscr.addstr(start + i, 2, f"{prefix}{num} {txt}", curses.A_REVERSE)
        else:
            txt = truncate_string_to_width(name, max_w)
            stdscr.addstr(start + i, 2, f"{prefix}{num} {txt}")

    footer = "ENTER: Play | p: Pause | n/b: Next/Prev | l: Loop | q: Quit"
    stdscr.addstr(h - 2, 2, truncate_string_to_width(footer, w - 4))
    stdscr.noutrefresh()

def player_tui(stdscr, folder_path, config):
    curses.curs_set(0)
    stdscr.timeout(100)

    playlist = sorted(
        os.path.join(folder_path, f)
        for f in os.listdir(folder_path)
        if f.lower().endswith(supported_exts)
    )

    if not playlist:
        draw_message_box(stdscr, "No audio files found.")
        return

    seen = load_seen_songs()
    new_songs_indices = []
    now = datetime.now()

    if folder_path not in seen:
        seen[folder_path] = {os.path.basename(p): now.isoformat() for p in playlist}
    else:
        for i, p in enumerate(playlist):
            name = os.path.basename(p)
            if name not in seen[folder_path]:
                new_songs_indices.append(i)
                seen[folder_path][name] = now.isoformat()

    init()

    current_player_id = None
    playing_idx = -1
    selected_idx = 0
    playlist_view_offset = 0

    song_lock = False
    is_paused = False
    was_playing = False

    now_scroll = 0
    sel_scroll = 0
    scroll_tick = 0
    last_sel = -1

    def play_song(idx):
        nonlocal current_player_id, playing_idx, is_paused, was_playing

        if current_player_id:
            stop(current_player_id)
            destroy(current_player_id)

        current_player_id = create_audio_player(playlist[idx])
        set_looping(current_player_id, song_lock)
        play(current_player_id)

        playing_idx = idx
        is_paused = False
        was_playing = True

    while True:
        h, _ = stdscr.getmaxyx()
        ph = h - 7

        if selected_idx >= playlist_view_offset + ph:
            playlist_view_offset = selected_idx - ph + 1
        elif selected_idx < playlist_view_offset:
            playlist_view_offset = selected_idx

        if selected_idx != last_sel:
            sel_scroll = 0
            last_sel = selected_idx

        if current_player_id:
            playing_now = is_playing(current_player_id)

            if was_playing and not playing_now and not is_paused:
                if not song_lock:
                    next_idx = (playing_idx + 1) % len(playlist)
                    play_song(next_idx)

            was_playing = playing_now

        draw_player_tui(
            stdscr,
            playlist,
            selected_idx,
            playing_idx,
            playlist_view_offset,
            now_scroll,
            sel_scroll,
            song_lock,
            new_songs_indices,
            is_paused
        )

        scroll_tick += 1
        if scroll_tick >= 3:
            now_scroll += 1
            sel_scroll += 1
            scroll_tick = 0

        curses.doupdate()
        key = stdscr.getch()

        if key == -1:
            continue
        elif key == curses.KEY_UP:
            selected_idx = max(0, selected_idx - 1)
        elif key == curses.KEY_DOWN:
            selected_idx = min(len(playlist) - 1, selected_idx + 1)
        elif key in (10, 13):
            play_song(selected_idx)
        elif key == ord('p') and current_player_id:
            pause(current_player_id)
            is_paused = not is_paused
        elif key == ord('n'):
            if playing_idx != -1:
                next_idx = (playing_idx + 1) % len(playlist)
                play_song(next_idx)
        elif key == ord('b'):
            if playing_idx != -1:
                prev_idx = (playing_idx - 1) % len(playlist)
                play_song(prev_idx)
        elif key == ord('l'):
            song_lock = not song_lock
            if current_player_id:
                set_looping(current_player_id, song_lock)
        elif key == ord('C'):
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
        elif key == ord('q'):
            save_seen_songs(seen)
            cleanup()
            break
