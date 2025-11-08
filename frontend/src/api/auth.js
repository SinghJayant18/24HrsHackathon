import api from "./client";

export const registerOwner = async (payload) => {
  const { data } = await api.post("/auth/register", payload);
  return data;
};

export const loginOwner = async (payload) => {
  const { data } = await api.post("/auth/login", payload);
  return data;
};

export const getCurrentOwner = async (token) => {
  const { data } = await api.get("/auth/me", {
    headers: {
      Authorization: `Bearer ${token}`,
    },
  });
  return data;
};

