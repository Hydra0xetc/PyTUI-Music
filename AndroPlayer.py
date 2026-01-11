import ctypes
import os
import platform
from ctypes import c_void_p, c_char_p, c_bool, c_int
from typing import Optional, Dict, Tuple

# Global dictionary untuk melacak player
players: Dict[int, c_void_p] = {}
next_player_id = 1

# Load library sekali
lib = None

def _load_library(library_path: Optional[str] = None) -> ctypes.CDLL:
    """Load shared library (lazy loading)"""
    global lib
    
    if lib is not None:
        return lib
    
    if library_path:
        lib = ctypes.CDLL(library_path)
    else:
        # Tentukan nama library berdasarkan platform
        system = platform.system().lower()
        lib_name = "libAndroPlayer.so"
        
        # Cari di beberapa lokasi
        search_paths = [
            os.path.join(os.path.dirname(__file__), lib_name),
            os.path.join(".", lib_name),
            os.path.join("./lib/", lib_name),
            os.path.join("./audio/", lib_name),
            os.path.join("/usr/local/lib", lib_name),
            os.path.join("/usr/lib", lib_name),
        ]
        
        for path in search_paths:
            if os.path.exists(path):
                lib = ctypes.CDLL(path)
                break
        
        if lib is None:
            raise FileNotFoundError(f"Cannot find audio player library: {lib_name}")
    
    # Setup function prototypes
    _setup_prototypes(lib)
    return lib

def _setup_prototypes(lib: ctypes.CDLL):
    """Setup function prototypes untuk ctypes"""
    lib.createAudioPlayer.argtypes = [c_char_p]
    lib.createAudioPlayer.restype = c_void_p
    
    lib.setupUriAudioPlayer.argtypes = [c_void_p, c_char_p]
    lib.setupUriAudioPlayer.restype = None
    
    lib.playAudio.argtypes = [c_void_p]
    lib.playAudio.restype = None
    
    lib.pauseAudio.argtypes = [c_void_p]
    lib.pauseAudio.restype = None
    
    lib.stopAudio.argtypes = [c_void_p]
    lib.stopAudio.restype = None
    
    lib.setLooping.argtypes = [c_void_p, c_bool]
    lib.setLooping.restype = None
    
    lib.isAudioPlaying.argtypes = [c_void_p]
    lib.isAudioPlaying.restype = c_bool
    
    lib.destroyAudioPlayer.argtypes = [c_void_p]
    lib.destroyAudioPlayer.restype = None

def init(library_path: Optional[str] = None):
    """Initialize audio player library"""
    global lib
    lib = _load_library(library_path)

def create_audio_player(file_path: str) -> int:
    """
    Buat audio player baru.
    
    Args:
        file_path: Path ke file audio
        
    Returns:
        Player ID (integer)
    """
    global next_player_id, players
    
    if lib is None:
        init()
    
    file_path_bytes = file_path.encode('utf-8')
    player_ptr = lib.createAudioPlayer(file_path_bytes)
    
    if not player_ptr:
        raise RuntimeError(f"Failed to create audio player for: {file_path}")
    
    # Setup URI player
    lib.setupUriAudioPlayer(player_ptr, file_path_bytes)
    
    player_id = next_player_id
    players[player_id] = player_ptr
    next_player_id += 1
    
    return player_id

def play(player_id: int):
    """Mulai pemutaran audio"""
    if lib is None:
        raise RuntimeError("Audio player not initialized. Call init() first.")
    
    if player_id in players:
        lib.playAudio(players[player_id])

def pause(player_id: int):
    """Jeda pemutaran audio"""
    if lib is None:
        raise RuntimeError("Audio player not initialized. Call init() first.")
    
    if player_id in players:
        lib.pauseAudio(players[player_id])

def stop(player_id: int):
    """Hentikan pemutaran audio"""
    if lib is None:
        raise RuntimeError("Audio player not initialized. Call init() first.")
    
    if player_id in players:
        lib.stopAudio(players[player_id])

def set_looping(player_id: int, loop: bool):
    """Atur looping"""
    if lib is None:
        raise RuntimeError("Audio player not initialized. Call init() first.")
    
    if player_id in players:
        lib.setLooping(players[player_id], loop)

def is_playing(player_id: int) -> bool:
    """Cek apakah sedang memutar"""
    if lib is None:
        raise RuntimeError("Audio player not initialized. Call init() first.")
    
    if player_id in players:
        return lib.isAudioPlaying(players[player_id])
    return False

def destroy(player_id: int):
    """Hancurkan player"""
    if lib is None:
        raise RuntimeError("Audio player not initialized. Call init() first.")
    
    if player_id in players:
        lib.destroyAudioPlayer(players[player_id])
        del players[player_id]

def destroy_all():
    """Hancurkan semua player"""
    if lib is None:
        return
    
    for player_id in list(players.keys()):
        destroy(player_id)

def cleanup():
    """Cleanup semua resources"""
    destroy_all()
    global lib
    lib = None
