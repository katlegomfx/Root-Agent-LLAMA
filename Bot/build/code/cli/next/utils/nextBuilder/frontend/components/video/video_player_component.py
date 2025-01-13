# utils\nextBuilder\frontend\components\video\video_player_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    write_to_file,
    COMPONENT_DIR,
    app_name,

)

def create_video_viewer_component():
    component_content = f"""'use client'
import React from 'react';
import PropTypes from 'prop-types';
import YouTube from 'react-youtube';

export default function VideoPlayer () {{
  const opts = {{
    height: '390',
    width: '640',
    playerVars: {{
      autoplay: 1,
    }},
  }};

  const onReady = (event) => {{
    // Access to player in all event handlers via event.target
    event.target.pauseVideo();
  }};

  return (
    <div>
      <h3>{{title}}</h3>
      <YouTube
        videoId={{file_path}}
        opts={{opts}}
        onReady={{onReady}}
      />
    </div>
  );
;
}}
"""
    file_path = os.path.join(app_name, COMPONENT_DIR, 'VideoPlayer.jsx')
    write_to_file(file_path, component_content)


create_video_viewer_component()
