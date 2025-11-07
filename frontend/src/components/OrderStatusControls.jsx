import { useState } from "react";
import { OrderStatusBadge } from "./OrderStatusBadge.jsx";

const statuses = ["placed", "processing", "dispatched", "delivered", "cancelled"];

function OrderStatusControls({ order, onUpdateStatus, onAssignTracking, loadingStatus, loadingTracking }) {
  const [trackingId, setTrackingId] = useState(order?.tracking_id || "");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");

  if (!order) return null;

  return (
    <div className="space-y-4">
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-sm font-semibold text-slate-600">Order #{order.id}</h3>
            <p className="text-xs text-slate-500">Customer: {order.customer?.name}</p>
          </div>
          <OrderStatusBadge status={order.status} />
        </div>
        <div className="mt-3 grid gap-2 text-sm text-slate-600">
          <p>Total amount: ₹ {order.total_amount?.toFixed(2)}</p>
          <p>Email: {order.customer?.email}</p>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="text-sm font-semibold text-slate-600">Update Status</h4>
        <div className="mt-3 flex flex-wrap gap-2">
          {statuses.map((status) => (
            <button
              key={status}
              onClick={() => onUpdateStatus(status)}
              disabled={loadingStatus}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                order.status === status
                  ? "bg-primary text-white"
                  : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
              }`}
            >
              {status.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="text-sm font-semibold text-slate-600">Assign Tracking</h4>
        <div className="mt-3 grid gap-3 sm:grid-cols-4">
          <div className="sm:col-span-2">
            <label className="text-xs uppercase text-slate-500">Tracking ID</label>
            <input
              value={trackingId}
              onChange={(e) => setTrackingId(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs uppercase text-slate-500">Latitude</label>
            <input
              value={lat}
              onChange={(e) => setLat(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
          </div>
          <div>
            <label className="text-xs uppercase text-slate-500">Longitude</label>
            <input
              value={lng}
              onChange={(e) => setLng(e.target.value)}
              className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
          </div>
        </div>
        <button
          onClick={() => onAssignTracking({ trackingId, lat, lng })}
          disabled={loadingTracking}
          className="mt-3 rounded-lg bg-slate-900 px-4 py-2 text-sm font-semibold text-white hover:bg-slate-700 disabled:opacity-70"
        >
          {loadingTracking ? "Saving..." : "Save Tracking"}
        </button>
        {order.tracking_url ? (
          <p className="mt-2 text-xs text-slate-500">
            Tracking URL: <a className="text-primary" href={order.tracking_url} target="_blank" rel="noreferrer">Open Maps</a>
          </p>
        ) : null}
      </div>
    </div>
  );
}

export default OrderStatusControls;

