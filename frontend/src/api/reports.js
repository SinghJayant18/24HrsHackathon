import api from "./client";

export const fetchTaxSummary = async ({ period, date_ref }) => {
  const params = new URLSearchParams({ period });
  if (date_ref) params.append("date_ref", date_ref);
  const { data } = await api.get(`/reports/revenue/tax?${params.toString()}`);
  return data;
};

export const downloadRevenuePdf = async ({ period, date_ref }) => {
  const params = new URLSearchParams({ period });
  if (date_ref) params.append("date_ref", date_ref);
  const { data } = await api.get(`/reports/revenue/pdf?${params.toString()}`, {
    responseType: "blob"
  });
  return data;
};

