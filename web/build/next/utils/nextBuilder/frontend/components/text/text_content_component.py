# Bot\build\code\cli\next\utils\nextBuilder\frontend\components\text\text_content_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import write_to_file, app_name, COMPONENT_DIR  # nopep8

def create_text_content_component():
    component_content = f"""'use client'
import React, {{ useEffect, useState }} from 'react';
import {{ fetchBlogposts }} from '@/lib/utils/blogPosts';
import {{ fetchNewsposts }} from '@/lib/utils/newsPosts';
import {{ fetchEventsposts }} from '@/lib/utils/eventsPosts';

export default function TextContent ({{ identifier }}) {{
    const [records, setRecords] = useState(null);

    useEffect(() => {{
        fetchNewsposts().then(setRecords);
        if (identifier === 'blog') {{
            fetchBlogposts().then(setRecords);
        }} else if (identifier === 'events') {{
            fetchEventsposts().then(setRecords);
        }}
    }}, [identifier]);

    if (!records) return <div>Loading...</div>;

    return (
        <main className="pt-20 flex min-h-screen flex-col items-center justify-start p-10 bg-gray-100">
            <div className="w-full mb-6">
                <h1 className="text-2xl font-bold text-gray-800">Posts Page</h1>
            </div>
            <div className="w-full grid grid-cols-1 md:grid-cols-3 gap-4">
                
    {{records.map((record, index) => (
        <div key={{index}} className="bg-white p-6 rounded-lg shadow-md">
            <div className="text-black">user_id: {{record.user_id}}</div>
<div className="text-black">title: {{record.title}}</div>
<div className="text-black">content: {{record.content}}</div>
<div className="text-black">blog_status: {{record.blog_status}}</div>
<div className="text-black">tags: {{record.tags}}</div>
<div className="text-black">view_count: {{record.view_count}}</div>
<div className="text-black">order: {{record.order}}</div>
<div className="text-black">comments_count: {{record.comments_count}}</div>
<div className="text-black">image_path: {{record.image_path}}</div>
    
        </div>
    ))}}
    
            </div>
        </main>
    );
}};
"""
    file_path = os.path.join(app_name, COMPONENT_DIR, 'TextContent.jsx')
    write_to_file(file_path, component_content)

create_text_content_component()
