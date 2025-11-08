import { useMutation, useQuery } from "@tanstack/react-query";
import { fetchQuarterlySummary, sendTaxAlert, checkTaxAlerts } from "../api/taxes.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import { Mail, Calendar, AlertCircle, CheckCircle } from "lucide-react";
import { format } from "date-fns";

function Taxes() {
  const summaryQuery = useQuery({
    queryKey: ["taxes", "quarterly"],
    queryFn: fetchQuarterlySummary
  });

  const alertMutation = useMutation({
    mutationFn: sendTaxAlert,
    onSuccess: (data) => {
      alert(`Tax alert email sent to ${data.to}`);
    },
    onError: (err) => {
      alert(err.response?.data?.detail || "Failed to send alert. Please make sure you're logged in.");
    }
  });

  const checkAlertsMutation = useMutation({
    mutationFn: checkTaxAlerts,
    onSuccess: (data) => {
      if (data.alerts_sent.length > 0) {
        alert(`Tax alerts checked. ${data.alerts_sent.length} alert(s) sent.`);
      } else {
        alert(`No alerts due. Next deadline: ${new Date(data.next_deadline).toLocaleDateString()}`);
      }
    },
    onError: () => alert("Failed to check alerts")
  });

  const data = summaryQuery.data;

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Tax & GST Planner</h2>
          <p className="text-sm text-slate-500">
            Track quarterly revenue, estimated tax liability, and automated payment reminders.
          </p>
        </div>
        <div className="flex flex-wrap items-center gap-2">
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
        <ErrorState 
          message={summaryQuery.error?.response?.status === 401 
            ? "Please login to view tax information" 
            : "Failed to get tax summary"} 
          onRetry={() => summaryQuery.refetch()} 
        />
      ) : data ? (
        <div className="grid gap-6 lg:grid-cols-2">
          {/* Tax Summary */}
          <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
            <h3 className="text-lg font-semibold text-slate-800">Quarterly Tax Summary</h3>
            <p className="text-sm text-slate-500">Period: {data.period}</p>
            
            {/* Business Type Badge */}
            <div className="mt-4">
              {data.gst_registered ? (
                <span className="inline-flex items-center gap-1 rounded-full bg-green-100 px-3 py-1 text-xs font-semibold text-green-800">
                  <CheckCircle className="h-3 w-3" />
                  GST Registered Business
                </span>
              ) : (
                <span className="inline-flex items-center gap-1 rounded-full bg-blue-100 px-3 py-1 text-xs font-semibold text-blue-800">
                  <AlertCircle className="h-3 w-3" />
                  Non-GST (Presumptive Tax)
                </span>
              )}
            </div>

            <div className="mt-6 space-y-4">
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500">Quarterly Revenue</p>
                <p className="mt-2 text-3xl font-semibold text-slate-800">
                  ₹ {data.revenue?.toFixed(2) || "0.00"}
                </p>
              </div>

              {/* Tax Breakdown */}
              <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                <p className="text-sm uppercase text-slate-500 mb-3">Tax Breakdown</p>
                <div className="space-y-2">
                  {data.breakdown && Object.entries(data.breakdown).map(([key, value]) => (
                    <div key={key} className="flex justify-between text-sm">
                      <span className="text-slate-600">{key}</span>
                      <span className="font-semibold text-slate-800">₹ {Number(value).toFixed(2)}</span>
                    </div>
                  ))}
                </div>
              </div>

              <div className="rounded-lg border-2 border-primary bg-primary/5 p-4">
                <p className="text-sm uppercase text-slate-500">Total Tax Due</p>
                <p className="mt-2 text-3xl font-bold text-primary">
                  ₹ {data.total_tax?.toFixed(2) || "0.00"}
                </p>
              </div>
            </div>
          </div>

          {/* Deadline & Alerts */}
          <div className="space-y-6">
            {/* Payment Deadline */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-800 flex items-center gap-2">
                <Calendar className="h-5 w-5 text-primary" />
                Payment Deadline
              </h3>
              <div className="mt-4 space-y-3">
                <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Next Deadline</p>
                  <p className="mt-1 text-xl font-semibold text-slate-800">
                    {data.tax_deadline ? format(new Date(data.tax_deadline), "dd MMMM yyyy") : "N/A"}
                  </p>
                </div>
                <div className="rounded-lg border border-slate-100 bg-slate-50 p-4">
                  <p className="text-sm text-slate-500">Days Remaining</p>
                  <p className={`mt-1 text-xl font-semibold ${
                    (data.days_until_deadline || 0) < 30 ? "text-red-600" : 
                    (data.days_until_deadline || 0) < 60 ? "text-orange-600" : 
                    "text-green-600"
                  }`}>
                    {data.days_until_deadline || 0} days
                  </p>
                </div>
              </div>
            </div>

            {/* Tax Alerts */}
            <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
              <h3 className="text-lg font-semibold text-slate-800">Tax Alerts</h3>
              <p className="text-sm text-slate-500 mt-1">
                Automated alerts sent to your registered email (15 weeks before and 1 week before deadline).
              </p>
              <div className="mt-4 space-y-3">
                <button
                  onClick={() => alertMutation.mutate()}
                  disabled={alertMutation.isPending}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-lg bg-primary px-4 py-3 text-sm font-semibold text-white shadow hover:bg-primary/90 disabled:opacity-60"
                >
                  <Mail className="h-4 w-4" />
                  {alertMutation.isPending ? "Sending..." : "Send Tax Alert Now"}
                </button>
                <button
                  onClick={() => checkAlertsMutation.mutate()}
                  disabled={checkAlertsMutation.isPending}
                  className="w-full inline-flex items-center justify-center gap-2 rounded-lg border border-slate-200 bg-white px-4 py-3 text-sm font-semibold text-slate-700 shadow-sm hover:bg-slate-50 disabled:opacity-60"
                >
                  <AlertCircle className="h-4 w-4" />
                  {checkAlertsMutation.isPending ? "Checking..." : "Check Scheduled Alerts"}
                </button>
                <p className="text-xs text-slate-500">
                  Alerts are automatically sent 15 weeks before and 1 week before the deadline.
                </p>
              </div>
            </div>
          </div>
        </div>
      ) : null}
    </div>
  );
}

export default Taxes;

