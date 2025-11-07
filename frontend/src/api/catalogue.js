import api from "./client";

export const fetchCatalogue = async () => {
  const { data } = await api.get("/catalogue/");
  return data;
};

