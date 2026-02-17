import axios from 'axios';

const API_BASE_URL = 'http://localhost:8000/api';

const api = axios.create({
    baseURL: API_BASE_URL,
});

export const healthApi = {
    // Single call for the full pipeline
    completeAnalysis: async (file) => {
        const formData = new FormData();
        formData.append('file', file);

        try {
            const response = await api.post('/complete-analysis', formData, {
                headers: {
                    'Content-Type': 'multipart/form-data',
                },
            });
            return response.data;
        } catch (error) {
            console.error("Error in completeAnalysis:", error);
            throw error;
        }
    },

    // Individual steps if needed
    extractFromFile: async (file) => {
        const formData = new FormData();
        formData.append('file', file);
        const response = await api.post('/extract-from-file', formData);
        return response.data;
    },

    analyzeHealth: async (data) => {
        const response = await api.post('/analyze-health', data);
        return response.data;
    },

    generateDietPlan: async (data) => {
        const response = await api.post('/generate-diet-plan', data);
        return response.data;
    }
};

export default api;
