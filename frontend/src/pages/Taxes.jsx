import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchMonthlySummary, sendTaxAlert } from "../api/taxes.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import { Mail } from "lucide-react";

function Taxes() {
  const now = new Date();
  const [month, setMonth] = useState(now.getMonth() + 1);
  const [year, setYear] = useState(now.getFullYear());
  const [email, setEmail] = useState("");

  const summaryQuery = useQuery({
    queryKey: ["taxes", month, year],
    queryFn: () => fetchMonthlySummary({ month, year })
  });

  const alertMutation = useMutation({
    mutationFn: sendTaxAlert,
    onSuccess: () => alert("Tax alert email sent."),
    onError: () => alert("Failed to send alert")
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Tax & GST Planner</h2>
          <p className="text-sm text-slate-500">
            Track monthly revenue, estimated tax liability, and email yourself reminders.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
          <select
            value={month}
            onChange={(e) => setMonth(Number(e.target.value))}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
          >
            {Array.from({ length: 12 }).map((_, idx) => (
              <option key={idx} value={idx + 1}>
                {new Date(0, idx).toLocaleString("default", { month: "long" })}
              </option>
            ))}
          </select>
          <input
            type="number"
            value={year}
            onChange={(e) => setYear(Number(e.target.value))}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            placeholder="Year"
          />
          <button
            onClick={() => summaryQuery.refetch()}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            Refresh
          </button>
        </div>
      </div>

      {summaryQuery.isLoading ? (
        <LoadingSpinner label="Calculating taxes..." />
      ) : summaryQuery.isError ? (
        <ErrorState message="Failed to get tax summary" onRetry={() => summaryQuery.refetch()} />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Monthly Summary</h3>
            <p className="text-sm text-slate-500">Period: {summaryQuery.data.period}</p>
            <div className="mt-6 space-y-4">
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500">Revenue</p>
                <p className="mt-2 text-3xl font-semibold text-slate-800">
                  ₹ {summaryQuery.data.revenue.toFixed(2)}
                </p>
              </div>
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500">Tax Rate</p>
                <p className="mt-2 text-3xl font-semibold text-slate-800">
                  {summaryQuery.data.tax_rate_percent}%
                </p>
              </div>
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500">Estimated Tax Due</p>
                <p className="mt-2 text-3xl font-semibold text-slate-800">
                  ₹ {summaryQuery.data.tax_due.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Send Tax Reminder</h3>
            <p className="text-sm text-slate-500">
              Email the owner with automated GST/tax reminders and due amount.
            </p>
            <div className="mt-4 space-y-4">
              <div>
                <label className="text-xs uppercase text-slate-500">Recipient Email</label>
                <input
                  type="email"
                  value={email}
                  onChange={(e) => setEmail(e.target.value)}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                  placeholder="owner@example.com"
                />
              </div>
              <button
                onClick={() =>
                  alertMutation.mutate({ to_email: email || undefined, month, year })
                }
                disabled={alertMutation.isLoading}
                className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary/90 disabled:opacity-60"
              >
                <Mail className="h-4 w-4" />
                {alertMutation.isLoading ? "Sending..." : "Send Alert"}
              </button>
              <p className="text-xs text-slate-500">
                Uses backend automation to generate reminder email with revenue + tax due and due
                date information.
              </p>
            </div>
          </div>
        </div>
      )}
    </div>
  );
}

export default Taxes;

