import api from "./client";

export const fetchQuarterlySummary = async () => {
  const { data } = await api.get("/taxes/quarterly-summary");
  return data;
};

export const fetchMonthlySummary = async ({ month, year }) => {
  const params = new URLSearchParams();
  if (month) params.append("month", month);
  if (year) params.append("year", year);
  const { data } = await api.get(`/taxes/monthly-summary?${params.toString()}`);
  return data;
};

export const sendTaxAlert = async () => {
  const { data } = await api.post("/taxes/send-tax-alert");
  return data;
};

export const checkTaxAlerts = async () => {
  const { data } = await api.get("/taxes/check-alerts");
  return data;
};

