import React, { useState, useEffect } from 'react';
import api from '../services/api';

function UploadPage({ refreshStats }) {
  const [dragActive, setDragActive] = useState(false);
  const [selectedFile, setSelectedFile] = useState(null);
  const [uploading, setUploading] = useState(false);
  const [uploadStatus, setUploadStatus] = useState({ success: null, message: '' });
  
  const [documents, setDocuments] = useState([]);
  const [loadingDocs, setLoadingDocs] = useState(false);

  const loadDocuments = async () => {
    setLoadingDocs(true);
    try {
      const data = await api.getDocuments();
      setDocuments(data || []);
    } catch (err) {
      console.error("Failed to load documents", err);
    } finally {
      setLoadingDocs(false);
    }
  };

  useEffect(() => {
    loadDocuments();
  }, []);

  const handleDrag = (e) => {
    e.preventDefault();
    e.stopPropagation();
    if (e.type === "dragenter" || e.type === "dragover") {
      setDragActive(true);
    } else if (e.type === "dragleave") {
      setDragActive(false);
    }
  };

  const validateFile = (file) => {
    if (!file) return false;
    const name = file.name.toLowerCase();
    const allowed = ['.pdf', '.docx', '.txt', '.md'];
    return allowed.some(ext => name.endsWith(ext));
  };

  const handleDrop = (e) => {
    e.preventDefault();
    e.stopPropagation();
    setDragActive(false);
    
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      processFileSelection(e.dataTransfer.files[0]);
    }
  };

  const handleFileChange = (e) => {
    if (e.target.files && e.target.files[0]) {
      processFileSelection(e.target.files[0]);
    }
  };

  const processFileSelection = (file) => {
    if (validateFile(file)) {
      setSelectedFile(file);
      setUploadStatus({ success: null, message: '' });
    } else {
      setUploadStatus({ success: false, message: 'Invalid file format. Supported: .pdf, .docx, .txt, .md' });
    }
  };

  const handleIngest = async () => {
    if (!selectedFile) return;
    setUploading(true);
    setUploadStatus({ success: null, message: '' });
    
    try {
      const response = await api.uploadDocument(selectedFile);
      setUploadStatus({
        success: true,
        message: `Successfully uploaded! Processed ${response.data.chunk_count} chunks.`
      });
      setSelectedFile(null);
      
      await loadDocuments();
      if (refreshStats) await refreshStats();
    } catch (err) {
      console.error(err);
      setUploadStatus({
        success: false,
        message: `Upload failed: ${err.message || 'Unknown error occurred.'}`
      });
    } finally {
      setUploading(false);
    }
  };

  const handleDelete = async (docId, filename) => {
    if (!window.confirm(`Are you sure you want to delete ${filename}?`)) {
      return;
    }
    
    try {
      await api.deleteDocument(docId);
      await loadDocuments();
      if (refreshStats) await refreshStats();
    } catch (err) {
      alert(`Failed to delete document: ${err.message}`);
    }
  };

  return (
    <div className="space-y-6">
      
      {/* Header */}
      <div className="bg-white p-6 rounded-lg shadow flex justify-between items-center border border-gray-200">
        <div>
          <h2 className="text-2xl font-bold text-gray-800">Upload Documents</h2>
          <p className="text-sm text-gray-500 mt-1">Upload and manage your data sources.</p>
        </div>
        <button
          onClick={loadDocuments}
          disabled={loadingDocs}
          className="bg-blue-600 text-white px-4 py-2 rounded-md hover:bg-blue-700 disabled:opacity-50 transition-colors"
        >
          {loadingDocs ? 'Refreshing...' : 'Refresh Files'}
        </button>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        
        {/* Upload Zone */}
        <div className="lg:col-span-2 bg-white rounded-lg shadow border border-gray-200 p-6">
          <h3 className="text-lg font-bold text-gray-700 mb-4">File Upload</h3>
          
          <div 
            onDragEnter={handleDrag}
            onDragOver={handleDrag}
            onDragLeave={handleDrag}
            onDrop={handleDrop}
            className={`border-2 border-dashed rounded-lg p-10 flex flex-col items-center justify-center text-center transition-colors ${
              dragActive 
                ? 'border-blue-500 bg-blue-50' 
                : 'border-gray-300 hover:border-blue-400 hover:bg-gray-50'
            }`}
          >
            <input 
              type="file" 
              id="file-upload"
              onChange={handleFileChange}
              accept=".pdf,.docx,.txt,.md"
              className="hidden"
            />
            <label htmlFor="file-upload" className="cursor-pointer flex flex-col items-center">
              <span className="text-blue-600 font-semibold mb-2">Click to upload or drag and drop</span>
              <span className="text-sm text-gray-500">PDF, DOCX, TXT, MD (Max 50MB)</span>
            </label>
          </div>

          {selectedFile && (
            <div className="mt-6 p-4 border border-gray-200 rounded-md flex justify-between items-center bg-gray-50">
              <div>
                <p className="font-semibold text-gray-800">{selectedFile.name}</p>
                <p className="text-xs text-gray-500">{(selectedFile.size / 1024 / 1024).toFixed(2)} MB</p>
              </div>
              <button
                onClick={handleIngest}
                disabled={uploading}
                className="bg-green-600 text-white px-4 py-2 rounded-md hover:bg-green-700 disabled:opacity-50 transition-colors font-medium"
              >
                {uploading ? 'Processing...' : 'Upload File'}
              </button>
            </div>
          )}

          {uploadStatus.message && (
            <div className={`mt-4 p-4 rounded-md text-sm ${
              uploadStatus.success ? 'bg-green-100 text-green-700' : 'bg-red-100 text-red-700'
            }`}>
              {uploadStatus.message}
            </div>
          )}
        </div>

        {/* Document List */}
        <div className="bg-white rounded-lg shadow border border-gray-200 overflow-hidden h-fit max-h-[600px] flex flex-col">
          <div className="bg-gray-50 px-6 py-4 border-b border-gray-200">
            <h3 className="text-lg font-bold text-gray-700">Indexed Files</h3>
          </div>
          
          <div className="p-4 overflow-y-auto flex-1">
            {loadingDocs ? (
              <p className="text-center text-gray-500 py-8">Loading files...</p>
            ) : documents.length === 0 ? (
              <p className="text-center text-gray-500 py-8">No files uploaded yet.</p>
            ) : (
              <ul className="divide-y divide-gray-100">
                {documents.map((doc) => (
                  <li key={doc.doc_id} className="py-3 flex justify-between items-center">
                    <div className="overflow-hidden mr-4">
                      <p className="font-medium text-gray-800 truncate text-sm" title={doc.filename}>
                        {doc.filename}
                      </p>
                      <p className="text-xs text-gray-500 mt-1">Chunks: {doc.chunk_count}</p>
                    </div>
                    <button
                      onClick={() => handleDelete(doc.doc_id, doc.filename)}
                      className="text-red-500 hover:text-red-700 text-sm font-medium px-2 py-1 hover:bg-red-50 rounded transition-colors"
                    >
                      Delete
                    </button>
                  </li>
                ))}
              </ul>
            )}
          </div>
        </div>

      </div>
    </div>
  );
}

export default UploadPage;