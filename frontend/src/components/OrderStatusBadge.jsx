const statusStyles = {
  placed: "bg-slate-100 text-slate-700",
  processing: "bg-blue-100 text-blue-700",
  dispatched: "bg-amber-100 text-amber-700",
  delivered: "bg-emerald-100 text-emerald-700",
  cancelled: "bg-red-100 text-red-600"
};

export function OrderStatusBadge({ status }) {
  return (
    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${statusStyles[status] || ""}`}>
      {status?.toUpperCase()}
    </span>
  );
}

