# utils\nextBuilder\frontend\components\text\text_viewer_component.py
import sys
import os



sys.path.append(os.getcwd())

from utils.shared import (  # nopep8
    write_to_file,
    COMPONENT_DIR,
    app_name,

)

# Assuming the utils.shared module provides necessary utilities for file operations


def create_text_viewer_component():
    component_content = f"""'use client'
import React from 'react';
import PropTypes from 'prop-types';

const TextViewer = ({{
    content,
    title
}}) => {{
    return (
        <div className="text-viewer">
            <h1>{{title}}</h1>
            <p>{{content}}</p>
        </div>
    );
}};

TextViewer.propTypes = {{
    content: PropTypes.string.isRequired,
    title: PropTypes.string.isRequired,
}};

export default TextViewer;
"""
    file_path = os.path.join(app_name, COMPONENT_DIR, 'TextViewer.jsx')
    write_to_file(file_path, component_content)


create_text_viewer_component()
