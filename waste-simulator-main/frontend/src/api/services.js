import apiClient from "./apiClient";

export const authService = {
  login: (email, password) => apiClient.post("/auth/login", { email, password }),
  register: (data) => apiClient.post("/auth/register", data),
  getMe: () => apiClient.get("/auth/me"),
};

export const userService = {
  list: () => apiClient.get("/users"),
  create: (data) => apiClient.post("/users", data),
  update: (id, data) => apiClient.put(`/users/${id}`, data),
  delete: (id) => apiClient.delete(`/users/${id}`),
};

export const locationService = {
  list: () => apiClient.get("/locations"),
  getById: (id) => apiClient.get(`/locations/${id}`),
  create: (data) => apiClient.post("/locations", data),
  update: (id, data) => apiClient.put(`/locations/${id}`, data),
  listHabitations: (locationId) => apiClient.get(`/habitations?location_id=${locationId}`),
  createHabitation: (data) => apiClient.post("/habitations", data),
};

export const parameterService = {
  getDemography: (locationId) => apiClient.get(`/parameters/demography/${locationId}`),
  saveDemography: (locationId, data) => apiClient.post(`/parameters/demography/${locationId}`, data),
  getInfrastructure: (locationId) => apiClient.get(`/parameters/infrastructure/${locationId}`),
  saveInfrastructure: (locationId, data) => apiClient.post(`/parameters/infrastructure/${locationId}`, data),
  getIndustrial: (locationId) => apiClient.get(`/parameters/industrial/${locationId}`),
  saveIndustrial: (locationId, data) => apiClient.post(`/parameters/industrial/${locationId}`, data),
  getComposition: (locationId) => apiClient.get(`/parameters/composition/${locationId}`),
  saveComposition: (locationId, data) => apiClient.post(`/parameters/composition/${locationId}`, data),
};

export const wasteService = {
  calculateComprehensive: (locationId) => apiClient.get(`/waste/comprehensive/${locationId}`),
  calculateLive: (data) => apiClient.post("/waste/calculate-live", data),
  listSources: (locationId) => apiClient.get(`/waste-sources?location_id=${locationId}`),
  createSource: (data) => apiClient.post("/waste-sources", data),
  deleteSource: (id) => apiClient.delete(`/waste-sources/${id}`),
};

export const facilityService = {
  list: (locationId) => apiClient.get(`/facilities?location_id=${locationId}`),
  create: (data) => apiClient.post("/facilities", data),
  delete: (id) => apiClient.delete(`/facilities/${id}`),
};

export const eventService = {
  list: (locationId) => apiClient.get(`/events?location_id=${locationId}`),
  create: (data) => apiClient.post("/events", data),
  delete: (id) => apiClient.delete(`/events/${id}`),
};

export const historicalService = {
  list: (locationId, params) => apiClient.get(`/historical-waste?location_id=${locationId}`, { params }),
  create: (data) => apiClient.post("/historical-waste", data),
  getAnalytics: (locationId, params) => apiClient.get(`/historical-waste/analytics/${locationId}`, { params }),
};

export const forecastService = {
  getEvaluation: (locationId, params) => apiClient.get(`/forecast/evaluation/${locationId}`, { params }),
  saveForecast: (data) => apiClient.post("/forecast", data),
};

export const simulationService = {
  listStrategies: (locationId) => apiClient.get(`/strategies?location_id=${locationId}`),
  createStrategy: (data) => apiClient.post("/strategies", data),
  listScenarios: (locationId) => apiClient.get(`/scenarios?location_id=${locationId}`),
  createScenario: (data) => apiClient.post("/scenarios", data),
  run: (data) => apiClient.post("/simulations/run", data),
  whatIf: (data) => apiClient.post("/simulations/what-if", data),
};

export const gisService = {
  getLayers: (locationId) => apiClient.get(`/gis/layers?location_id=${locationId}`),
  enrich: (locationId) => apiClient.get(`/gis/enrich/${locationId}`),
  enrichPost: (data) => apiClient.post("/gis/enrich", data),
};

export const chatService = {
  ask: (locationId, question) => apiClient.post("/chat", { location_id: locationId, question }),
};

export const reportService = {
  generate: (locationId, data) => apiClient.post(`/reports/generate/${locationId}`, data),
};

export const dataQualityService = {
  getReport: (locationId) => apiClient.get(`/data-quality/${locationId}`),
};

export const auditService = {
  list: (limit = 100) => apiClient.get(`/audit-logs?limit=${limit}`),
};
