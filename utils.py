import os
from wcwidth import wcswidth

def truncate_string_to_width(s, width):
    """Truncate string to fit visual width"""
    current_width = 0
    truncated_s = []
    for char in s:
        char_width = wcswidth(char)
        if current_width + char_width > width:  # Check visual width
            break
        current_width += char_width
        truncated_s.append(char)
    return "".join(truncated_s)

def get_scrolling_display_string(s, max_width, scroll_offset):
    """Returns the scrolling part of the string"""
    visual_width = wcswidth(s)
    if visual_width <= max_width:
        return s

    padding_chars = 3
    padded_s = s + (" " * padding_chars)
    start_char_idx = scroll_offset % len(padded_s)

    current_visual_width = 0
    display_chars = []
    for i in range(len(padded_s)):
        char_idx = (start_char_idx + i) % len(padded_s)
        char = padded_s[char_idx]
        char_visual_width = wcswidth(char)

        if current_visual_width + char_visual_width > max_width:
            break
        current_visual_width += char_visual_width
        display_chars.append(char)

    return "".join(display_chars)

def get_folders(path):
    if not os.path.isdir(path):
        return []
    return sorted([f for f in os.listdir(path) if os.path.isdir(os.path.join(path, f))])
