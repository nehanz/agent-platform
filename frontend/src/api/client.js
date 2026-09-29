import axios from "axios";

const API_BASE = import.meta.env.VITE_API_BASE || "http://localhost:8000";

const client = axios.create({ baseURL: API_BASE });

// Local dev: pick tenant via header
client.interceptors.request.use((config) => {
  const tenant = localStorage.getItem("tenant_id") || "tenantA";
  config.headers["X-Tenant-Id"] = tenant;
  return config;
});

export const sendChat = (message, history) =>
  client.post("/chat", { message, history }).then((r) => r.data);

export const sendApproval = (execution_id, approved) =>
  client.post("/approve", { execution_id, approved }).then((r) => r.data);

export const getAudit = (execution_id) =>
  client.get(`/audit/${execution_id}`).then((r) => r.data);

export const listAudits = () =>
  client.get("/audit").then((r) => r.data);