# utils\nextBuilder\frontend\components\video\video_content_component.py
import sys
import os


sys.path.append(os.getcwd())

from utils.shared import write_to_file, app_name, COMPONENT_DIR  # nopep8

def create_video_content_component():
    component_content = f"""'use client'
import React, {{ useEffect, useState }} from 'react';
import {{ fetchVideos }} from '@/lib/utils/videos';

export default function VideoContent () {{
    const [records, setRecords] = useState(null);

    useEffect(() => {{
        fetchVideos().then(setRecords);
    }}, []);

    if (!records) return <div>Loading...</div>;

        return (
        <main className="pt-20 flex min-h-screen flex-col items-center justify-start p-10 bg-gray-100">
            <div className="w-full mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Videos</h1>
            </div>
            <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-4">
                
    {{records.map((record, index) => (
        <div key={{index}} className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-black">type: {{record.type}}</div>
<div className="text-black">user_id: {{record.user_id}}</div>
<div className="text-black">channel: {{record.channel}}</div>
<div className="text-black">views_count: {{record.views_count}}</div>
<div className="text-black">genre: {{record.genre}}</div>
<div className="text-black">link: {{record.link}}</div>
<div className="text-black">title: {{record.title}}</div>
<div className="text-black">description: {{record.description}}</div>
<div className="text-black">file_path: {{record.file_path}}</div>
<div className="text-black">duration: {{record.duration}}</div>

    
        </div>
    ))}}
    
            </div>
        </main>
    );
}};
"""
    
    file_path = os.path.join(app_name, COMPONENT_DIR, 'VideoContent.jsx')
    write_to_file(file_path, component_content)

create_video_content_component()
