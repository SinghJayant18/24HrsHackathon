import api from "./client";

export const fetchItems = async () => {
  const { data } = await api.get("/items/");
  return data;
};

export const createItem = async (payload) => {
  const { data } = await api.post("/items/", payload);
  return data;
};

export const updateItem = async ({ id, payload }) => {
  const { data } = await api.patch(`/items/${id}`, payload);
  return data;
};

export const fetchItemById = async (id) => {
  const { data } = await api.get(`/items/${id}`);
  return data;
};

