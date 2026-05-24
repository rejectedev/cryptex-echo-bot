const rawUrl = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:5050';

// If Render provides only the host, we add the protocol
const API_BASE_URL = rawUrl.startsWith('http') ? rawUrl : `https://${rawUrl}`;

export default API_BASE_URL;
