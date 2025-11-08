import api from "./client";

export const fetchOrders = async () => {
  const { data } = await api.get("/orders/");
  return data;
};

export const createOrder = async (payload) => {
  const { data } = await api.post("/orders/", payload);
  return data;
};

export const getOrder = async (id) => {
  const { data } = await api.get(`/orders/${id}`);
  return data;
};

export const updateOrderStatus = async ({ id, status }) => {
  const { data } = await api.patch(`/orders/${id}/status`, { status });
  return data;
};

export const assignTracking = async ({ id, tracking_id, lat, lng }) => {
  const params = new URLSearchParams({ tracking_id });
  if (lat) params.append("lat", lat);
  if (lng) params.append("lng", lng);
  const { data } = await api.post(`/tracking/${id}/assign?${params.toString()}`);
  return data;
};

