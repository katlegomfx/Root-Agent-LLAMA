# Bot\build\code\cli\next\utils\nextBuilder\frontend\components\music\music_player_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    write_to_file,
    COMPONENT_DIR,
    app_name,

)

# Assuming the utils.shared module provides necessary utilities for file operations

def create_music_viewer_component():
    component_content = f"""'use client'

"""
    file_path = os.path.join(app_name, COMPONENT_DIR, 'MusicPlayer.jsx')
    write_to_file(file_path, component_content)

create_music_viewer_component()
