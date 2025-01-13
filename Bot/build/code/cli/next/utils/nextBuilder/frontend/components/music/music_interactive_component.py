# utils\nextBuilder\frontend\components\music\music_interactive_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import write_to_file, app_name, COMPONENT_DIR # nopep8

def create_interactive_comment_form():
    component_content = f"""'use client'
import React, {{ useState }} from 'react';
import useRedirectIfUnauthenticated from '@/components/deauthedWrapper';

const MusicCommentForm = ({{
    onSubmit
}}) => {{
    useRedirectIfUnauthenticated();
    const [comment, setComment] = useState('');

    const handleSubmit = (e) => {{
        e.preventDefault();
        onSubmit(comment);
        setComment('');
    }};

    return (
        <form onSubmit={{handleSubmit}}>
            <textarea
                value={{comment}}
                onChange={{(e) => setComment(e.target.value)}}
                required
            />
            <button type="submit">Submit Comment</button>
        </form>
    );
}};

export default MusicCommentForm;
"""
    file_path = os.path.join(app_name, COMPONENT_DIR, 'MusicCommentForm.jsx')
    write_to_file(file_path, component_content)

create_interactive_comment_form()
