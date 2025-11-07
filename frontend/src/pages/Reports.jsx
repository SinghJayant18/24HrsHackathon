import { useMutation, useQuery } from "@tanstack/react-query";
import { useState } from "react";
import { fetchTaxSummary, downloadRevenuePdf } from "../api/reports.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import { FileDown, CalendarRange } from "lucide-react";
import { format } from "date-fns";

const periodOptions = [
  { value: "day", label: "Daily" },
  { value: "month", label: "Monthly" },
  { value: "year", label: "Yearly" }
];

function Reports() {
  const today = format(new Date(), "yyyy-MM-dd");
  const [period, setPeriod] = useState("month");
  const [dateRef, setDateRef] = useState(today);

  const summaryQuery = useQuery({
    queryKey: ["tax-summary", period, dateRef],
    queryFn: () => fetchTaxSummary({ period, date_ref: dateRef })
  });

  const pdfMutation = useMutation({
    mutationFn: downloadRevenuePdf,
    onSuccess: (blob) => {
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement("a");
      a.href = url;
      a.download = `revenue_${period}_${dateRef || "current"}.pdf`;
      a.click();
      window.URL.revokeObjectURL(url);
    },
    onError: () => alert("Failed to download report")
  });

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Revenue Reports</h2>
          <p className="text-sm text-slate-500">
            Generate TSA-compliant revenue summaries and downloadable PDF reports
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-3">
          <select
            value={period}
            onChange={(e) => setPeriod(e.target.value)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
          >
            {periodOptions.map((opt) => (
              <option key={opt.value} value={opt.value}>
                {opt.label}
              </option>
            ))}
          </select>
          <div className="flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm">
            <CalendarRange className="h-4 w-4 text-slate-400" />
            <input
              type="date"
              value={dateRef}
              onChange={(e) => setDateRef(e.target.value)}
              className="border-none bg-transparent outline-none"
            />
          </div>
          <button
            onClick={() => summaryQuery.refetch()}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            Refresh
          </button>
        </div>
      </div>

      {summaryQuery.isLoading ? (
        <LoadingSpinner label="Loading revenue summary..." />
      ) : summaryQuery.isError ? (
        <ErrorState
          message="Failed to load revenue summary"
          onRetry={() => summaryQuery.refetch()}
        />
      ) : (
        <div className="grid gap-6 lg:grid-cols-2">
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Summary</h3>
            <p className="text-sm text-slate-500">Period: {summaryQuery.data.period}</p>
            <div className="mt-6 grid gap-4">
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500">Total Revenue</p>
                <p className="mt-2 text-3xl font-semibold text-slate-800">
                  ₹ {summaryQuery.data.total_revenue.toFixed(2)}
                </p>
              </div>
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500">
                  Estimated Tax ({summaryQuery.data.tax_rate_percent}%)
                </p>
                <p className="mt-2 text-3xl font-semibold text-slate-800">
                  ₹ {summaryQuery.data.total_tax_due.toFixed(2)}
                </p>
              </div>
            </div>
          </div>

          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Download Report</h3>
            <p className="text-sm text-slate-500">
              Generation uses backend PDF rendering; includes tax breakdown & totals.
            </p>
            <button
              onClick={() => pdfMutation.mutate({ period, date_ref: dateRef })}
              disabled={pdfMutation.isLoading}
              className="mt-6 inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary/90 disabled:opacity-60"
            >
              <FileDown className="h-4 w-4" />
              {pdfMutation.isLoading ? "Generating..." : "Download PDF"}
            </button>
            <p className="mt-3 text-xs text-slate-500">
              Tip: adjust the period/date above to generate daily, monthly, or yearly reports.
            </p>
          </div>
        </div>
      )}
    </div>
  );
}

export default Reports;

