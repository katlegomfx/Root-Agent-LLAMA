# Bot\build\code\cli\next\utils\nextBuilder\frontend\localFTP\components\ftp_ui_component.py
import sys
import os

sys.path.append(os.getcwd())

from utils.shared import create_component  # nopep8
FTP_TEMPLATE = """'use client'
import React, { useState, useEffect } from 'react';
import DropdownTreeSelect from 'react-dropdown-tree-select';
import 'react-dropdown-tree-select/dist/styles.css';

function FTPComponent() {
    const [files, setFiles] = useState([]);
    const [treeData, setTreeData] = useState([]);
    const [currentPath, setCurrentPath] = useState('.');
    const [uploadFileData, setUploadFileData] = useState({ localFile: null, remotePath: '' });
    const [downloadFilePath, setDownloadFilePath] = useState('');

    useEffect(() => {
        listFiles(currentPath);
    }, [currentPath]);

    const listFiles = async (path = '.') => {
        try {
            const response = await fetch(`http://localhost:5000/api/list-files?path=${encodeURIComponent(path)}`);
            const data = await response.json();
            setFiles(data);
            const formattedData = formatToTreeData(data);
            setTreeData(formattedData);
        } catch (error) {
            console.error('Error listing files:', error);
        }
    };

    const formatToTreeData = (files) => {
        return files.map(file => ({
            label: file, 
            value: file,
            children: [] // Placeholder for potential subdirectories
        }));
    };

    const handleFileSelect = (currentNode, selectedNodes) => {
        // Set the remote path based on selected node
        setUploadFileData({
            ...uploadFileData,
            remotePath: currentNode.value
        });
    };

    const uploadFile = async () => {
        try {
            const formData = new FormData();
            formData.append('file', uploadFileData.localFile);
            formData.append('remote_path', uploadFileData.remotePath); // Ensure this matches the Flask API's expected field
            const response = await fetch('http://localhost:5000/api/upload-file', {
                method: 'POST',
                body: formData,
            });
            const data = await response.json();
            console.log(data);
            listFiles(currentPath); // Refresh the file list
        } catch (error) {
            console.error('Error uploading file:', error);
        }
    };

    const downloadFile = async () => {
        try {
            // Constructing the file download URL dynamically
            const filePath = encodeURIComponent(downloadFilePath);
            const url = `/api/download-file?remote_path=${filePath}`;
            window.open(url, '_blank');
        } catch (error) {
            console.error('Error downloading file:', error);
        }
    };

    // Handlers for file input and path input
    const handleUploadFileChange = (event) => {
        setUploadFileData({
            ...uploadFileData,
            localFile: event.target.files[0],
        });
    };

    const handleUploadPathChange = (event) => {
        setUploadFileData({
            ...uploadFileData,
            remotePath: event.target.value,
        });
    };

    return (
        <div className="max-w-xl mx-auto p-4 bg-gray-100 rounded-lg shadow">
            <h2 className="text-lg font-semibold text-center text-blue-700 mb-4">FTP File Manager</h2>
        <div className="col">
            <DropdownTreeSelect 
                data={treeData} 
                onChange={handleFileSelect} 
                className="text-sm text-black"
                placeholderText="Select file or directory"
            />
            <ul className="list-disc pl-5">
                {files.map((file, index) => (
                    <li key={index} className="py-1 border-b border-gray-200 text-black">{file}</li>
                ))}
            </ul>
        </div>
        <div className="col">
            <div className="mb-4">
                <input type="file" onChange={handleUploadFileChange} className="block w-full text-sm text-gray-500 file:mr-4 file:py-2 file:px-4 file:rounded-full file:border-0 file:text-sm file:font-semibold file:bg-blue-50 file:text-blue-700 hover:file:bg-blue-100"/>
                <input type="text" placeholder="Remote path" value={uploadFileData.remotePath} onChange={handleUploadPathChange} className="mt-2 p-2 w-full rounded border-gray-300 shadow-sm"/>
                <button onClick={uploadFile} className="mt-2 px-4 py-2 bg-blue-500 text-white rounded hover:bg-blue-600 focus:outline-none focus:ring-2 focus:ring-blue-500 focus:ring-opacity-50">Upload File</button>
            </div>
            <div className="mb-4">
                <input type="text" placeholder="Download file path" value={downloadFilePath} onChange={e => setDownloadFilePath(e.target.value)} className="p-2 w-full rounded border-gray-300 shadow-sm"/>
                <button onClick={downloadFile} className="mt-2 px-4 py-2 bg-green-500 text-white rounded hover:bg-green-600 focus:outline-none focus:ring-2 focus:ring-green-500 focus:ring-opacity-50">Download File</button>
            </div>
        </div>

        </div>
    );
}

export default FTPComponent;
"""

create_component('FTPComponent', FTP_TEMPLATE)
