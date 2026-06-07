import axios from 'axios';

const API = `${process.env.REACT_APP_BACKEND_URL}/api`;

const apiClient = axios.create({
  baseURL: API,
  withCredentials: true,
});

export default apiClient;

// Users
export const getUsers = (role) => apiClient.get('/users', { params: { role } });
export const getUser = (userId) => apiClient.get(`/users/${userId}`);
export const updateUser = (userId, data) => apiClient.put(`/users/${userId}`, data);
export const deleteUser = (userId) => apiClient.delete(`/users/${userId}`);

// Agencies
export const getAgencies = () => apiClient.get('/agencies');
export const createAgency = (data) => apiClient.post('/agencies', data);
export const updateAgency = (agencyId, data) => apiClient.put(`/agencies/${agencyId}`, data);
export const deleteAgency = (agencyId) => apiClient.delete(`/agencies/${agencyId}`);

// Categories
export const getCategories = () => apiClient.get('/categories');
export const createCategory = (data) => apiClient.post('/categories', data);
export const deleteCategory = (categoryId) => apiClient.delete(`/categories/${categoryId}`);

// Subcategories
export const getSubcategories = (categoryId) => apiClient.get('/subcategories', { params: { category_id: categoryId } });
export const createSubcategory = (data) => apiClient.post('/subcategories', data);
export const deleteSubcategory = (subcategoryId) => apiClient.delete(`/subcategories/${subcategoryId}`);

// Service Categories
export const getServiceCategories = () => apiClient.get('/service-categories');
export const createServiceCategory = (data) => apiClient.post('/service-categories', data);
export const deleteServiceCategory = (serviceId) => apiClient.delete(`/service-categories/${serviceId}`);

// Investigations
export const getInvestigations = (params) => apiClient.get('/investigations', { params });
export const getInvestigation = (investigationId) => apiClient.get(`/investigations/${investigationId}`);
export const createInvestigation = (data) => apiClient.post('/investigations', data);
export const updateInvestigationStatus = (investigationId, status) => apiClient.put(`/investigations/${investigationId}/status`, { status });

// Services
export const updateService = (investigationId, serviceId, data) => apiClient.put(`/investigations/${investigationId}/services/${serviceId}`, data);

// Evidence
export const uploadEvidence = (investigationId, formData) => apiClient.post(`/investigations/${investigationId}/evidence`, formData, {
  headers: { 'Content-Type': 'multipart/form-data' },
});
export const getEvidence = (investigationId, serviceId) => apiClient.get(`/investigations/${investigationId}/evidence`, { params: { service_id: serviceId } });
export const getEvidenceLibrary = (investigationId) => apiClient.get(`/investigations/${investigationId}/evidence/library`);
export const updateEvidenceLinks = (evidenceId, serviceIds) => apiClient.put(`/evidence/${evidenceId}/link-services`, { service_ids: serviceIds });

// Findings
export const submitFindings = (investigationId, data) => apiClient.post(`/investigations/${investigationId}/findings`, data);
export const getFindings = (investigationId) => apiClient.get(`/investigations/${investigationId}/findings`);

// Rework
export const requestRework = (investigationId, data) => apiClient.post(`/investigations/${investigationId}/rework`, data);

// Activities
export const getActivities = (investigationId) => apiClient.get(`/investigations/${investigationId}/activities`);

// Notifications
export const getNotifications = () => apiClient.get('/notifications');
export const markNotificationRead = (notificationId) => apiClient.put(`/notifications/${notificationId}/read`);

// Dashboard
export const getDashboardStats = () => apiClient.get('/dashboard/stats');
