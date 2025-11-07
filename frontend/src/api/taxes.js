import api from "./client";

export const fetchMonthlySummary = async ({ month, year }) => {
  const params = new URLSearchParams();
  if (month) params.append("month", month);
  if (year) params.append("year", year);
  const { data } = await api.get(`/taxes/monthly-summary?${params.toString()}`);
  return data;
};

export const sendTaxAlert = async ({ to_email, month, year }) => {
  const params = new URLSearchParams();
  if (to_email) params.append("to_email", to_email);
  if (month) params.append("month", month);
  if (year) params.append("year", year);
  const { data } = await api.post(`/taxes/send-monthly-alert?${params.toString()}`);
  return data;
};

