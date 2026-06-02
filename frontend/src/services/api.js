const BASE_URL = '/api/v1';

const request = async (endpoint, options = {}) => {
  try {
    const response = await fetch(`${BASE_URL}${endpoint}`, options);
    
    if (!response.ok) {
      const errorData = await response.text();
      throw new Error(errorData || `HTTP error! status: ${response.status}`);
    }
    
    return await response.json();
  } catch (error) {
    console.error(`API Error (${endpoint}):`, error);
    throw error;
  }
};

const api = {
  getHealth: () => request('/health'),
  
  getSystemStatus: () => request('/system/status'),
  
  query: (query, topK = 5, threshold = 0.0) => request('/query', {
    method: 'POST',
    headers: {
      'Content-Type': 'application/json',
    },
    body: JSON.stringify({ query, top_k: topK, threshold })
  }),
  
  uploadDocument: (file) => {
    const formData = new FormData();
    formData.append('file', file);
    return request('/documents/upload', {
      method: 'POST',
      body: formData
    });
  },
  
  getDocuments: () => request('/documents'),
  
  deleteDocument: (docId) => request(`/documents/${docId}`, {
    method: 'DELETE'
  }),
  
  getMCPTools: () => request('/mcp/tools'),
  
  getMCPLogs: () => request('/mcp/log'),
  
  getSettings: () => request('/settings')
};

export default api;