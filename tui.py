import curses
import os
import subprocess
import shutil
from wcwidth import wcswidth
from utils import truncate_string_to_width, get_scrolling_display_string

def draw_menu(stdscr, selected_row_idx, items, title_text, help_text):
    h, w = stdscr.getmaxyx()
    stdscr.erase()
    stdscr.box()

    # Truncate and center the title
    max_line_width = max(1, w - 2) # Ensure min width of 1
    truncated_title = truncate_string_to_width(title_text, max_line_width)
    title_x = (w - wcswidth(truncated_title)) // 2
    if title_x < 1: title_x = 1 # Ensure x position is at least 1
    stdscr.addstr(1, title_x, truncated_title, curses.A_BOLD)
    
    # Ensure hline width is at least 1
    hline_width = max(1, w - 2)
    stdscr.hline(2, 1, curses.ACS_HLINE, hline_width)

    menu_h = h - 5
    start_line = 3
    
    # Left padding for menu items
    x = 2
    max_width = max(1, w - x - 2) # Max width for menu items, ensure min 1

    scroll_offset = 0
    if selected_row_idx >= menu_h:
        scroll_offset = selected_row_idx - menu_h + 1

    for i in range(menu_h):
        item_idx = i + scroll_offset
        if item_idx < len(items):
            item_name = items[item_idx]
            truncated_name = truncate_string_to_width(item_name, max_width)

            # Ensure y and x positions are valid before adding string
            if start_line + i < h and x < w:
                if item_idx == selected_row_idx:
                    stdscr.addstr(start_line + i, x, truncated_name, curses.A_REVERSE)
                else:
                    stdscr.addstr(start_line + i, x, truncated_name)

    # Truncate and center the help text
    truncated_help = truncate_string_to_width(help_text, max_line_width)
    help_x = (w - wcswidth(truncated_help)) // 2
    if help_x < 1: help_x = 1 # Ensure x position is at least 1
    
    # Ensure y and x positions are valid before adding string
    if h - 2 < h and help_x < w:
        stdscr.addstr(h - 2, help_x, truncated_help)
    stdscr.noutrefresh()

def draw_message_box(stdscr, message):
    """Draws a centered box with a left-aligned message and waits for a key press."""
    h, w = stdscr.getmaxyx()
    
    # Calculate max message width, considering box borders and padding
    max_msg_width = w - 8  # w - (2*border + 2*padding_left + 2*padding_right)
    if max_msg_width < 1: max_msg_width = 1 # Ensure it's at least 1

    truncated_message = truncate_string_to_width(message, max_msg_width)
    
    box_h = 5
    box_w = wcswidth(truncated_message) + 4 # 2 for padding, 2 for borders
    
    # Ensure box_w does not exceed terminal width
    if box_w > w: box_w = w
    if box_w < 10: box_w = 10 # Minimum width

    box_y = (h - box_h) // 2
    box_x = (w - box_w) // 2

    # Ensure box_x and box_y are within bounds
    if box_y < 0: box_y = 0
    if box_x < 0: box_x = 0

    # Create a new window for the box
    box_win = curses.newwin(box_h, box_w, box_y, box_x)
    box_win.box()
    
    # Add the message, left-aligned within the box
    # Ensure the message is placed correctly within the box's internal space
    msg_y = 2 # Vertical center of the box
    msg_x = 2 # Left padding inside the box
    box_win.addstr(msg_y, msg_x, truncated_message)
    
    box_win.refresh()
    box_win.getch() # wait for user to press a key

def check_dependencies():
    """Check if fd and fzf are installed."""
    return shutil.which("fd") is not None and shutil.which("fzf") is not None

def browse_path_tui(stdscr, start_path=None):
    """A TUI for browsing the filesystem using fd and fzf."""
    if not check_dependencies():
        draw_message_box(stdscr, "Please install 'fd' and 'fzf' for path selection.")
        return None

    # Exit curses mode to run fzf
    curses.endwin()

    selected_path = None
    try:
        # Run fd and pipe to fzf
        # Start searching from the user's home directory
        home_dir = os.path.expanduser("~")
        # We search for directories in the home directory.
        command = f"fd -L --type d . '{home_dir}' | fzf"
        
        # Using shell=True is necessary for the pipe
        process = subprocess.run(command, shell=True, capture_output=True, text=True, check=False)
        
        # fzf returns a non-zero exit code (130) when the user cancels (e.g., by pressing Esc).
        if process.returncode == 0:
            selected_path = process.stdout.strip()

    finally:
        # After the command, we need to get back into curses mode.
        # A simple refresh of the stdscr should do the trick.
        stdscr.refresh()


    return selected_path if selected_path else None

def get_text_input_tui(stdscr, prompt):
    input_text = ""
    try:
        curses.nocbreak()  # Temporarily disable cbreak
        curses.echo()      # Enable echoing
        stdscr.nodelay(False) # Blocking input for getstr

        stdscr.clear()
        stdscr.addstr(0, 0, prompt)
        stdscr.refresh()
        input_text = stdscr.getstr().decode('utf-8')

        # Confirmation step
        stdscr.addstr(2, 0, f"You entered: {input_text}")
        stdscr.addstr(3, 0, "Confirm? (y/n): ")
        stdscr.refresh()

        confirm_key = stdscr.getch()
        if confirm_key == ord('y'):
            return input_text
        else:
            return None  # User cancelled
    finally:
        curses.noecho()    # Disable echoing
        curses.cbreak()    # Re-enable cbreak
        stdscr.nodelay(True) # Set nodelay back to true
