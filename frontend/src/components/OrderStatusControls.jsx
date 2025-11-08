import { useState, useEffect } from "react";
import { OrderStatusBadge } from "./OrderStatusBadge.jsx";
import { Calendar, MapPin, Mail, Package, IndianRupee } from "lucide-react";

const statuses = ["placed", "processing", "dispatched", "delivered", "cancelled"];

function OrderStatusControls({ order, onUpdateStatus, onAssignTracking, loadingStatus, loadingTracking }) {
  const [trackingId, setTrackingId] = useState(order?.tracking_id || "");
  const [lat, setLat] = useState("");
  const [lng, setLng] = useState("");

  useEffect(() => {
    if (order) {
      setTrackingId(order.tracking_id || "");
    }
  }, [order]);

  if (!order) return null;

  const formatDate = (dateStr) => {
    if (!dateStr) return "N/A";
    try {
      return new Date(dateStr).toLocaleString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  const formatDeliveryDate = (dateStr) => {
    if (!dateStr) return "Not set";
    try {
      return new Date(dateStr).toLocaleString("en-IN", {
        day: "numeric",
        month: "short",
        year: "numeric",
        hour: "2-digit",
        minute: "2-digit",
      });
    } catch {
      return dateStr;
    }
  };

  // Calculate bill summary
  let subtotal = 0;
  let totalDiscount = 0;
  
  order.items?.forEach((oi) => {
    const priceAtPurchase = oi.price_at_purchase || 0;
    const quantity = oi.quantity || 0;
    const discountPct = oi.item?.discount_percent || 0;
    
    // Calculate original price before discount
    let originalPrice = priceAtPurchase;
    if (discountPct > 0) {
      originalPrice = priceAtPurchase / (1 - discountPct / 100);
    }
    
    // Calculate item totals
    const itemSubtotal = originalPrice * quantity;
    const itemDiscount = itemSubtotal * (discountPct / 100);
    
    subtotal += itemSubtotal;
    totalDiscount += itemDiscount;
  });
  
  const taxableAmount = subtotal - totalDiscount;
  const taxRate = 18; // 18% GST
  const taxAmt = taxableAmount * (taxRate / 100);
  const sgst = taxAmt / 2;
  const cgst = taxAmt / 2;
  const finalTotal = taxableAmount + taxAmt; // Subtotal - Discount + Tax

  return (
    <div className="space-y-4">
      {/* Order Header */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Order #{order.id}</h3>
            <p className="text-xs text-slate-500">Placed on {formatDate(order.created_at)}</p>
          </div>
          <OrderStatusBadge status={order.status} />
        </div>
      </div>

      {/* Customer Details */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="mb-3 text-sm font-semibold text-slate-600">Customer Details</h4>
        <div className="space-y-2 text-sm">
          <div className="flex items-center gap-2">
            <Package className="h-4 w-4 text-slate-400" />
            <span className="font-medium text-slate-700">{order.customer?.name}</span>
          </div>
          <div className="flex items-center gap-2">
            <Mail className="h-4 w-4 text-slate-400" />
            <span className="text-slate-600">{order.customer?.email}</span>
          </div>
          {order.customer?.address && (
            <div className="flex items-start gap-2">
              <MapPin className="mt-0.5 h-4 w-4 text-slate-400" />
              <span className="text-slate-600">{order.customer.address}</span>
            </div>
          )}
          {order.customer?.phone && (
            <div className="text-slate-600">Phone: {order.customer.phone}</div>
          )}
        </div>
      </div>

      {/* Expected Delivery */}
      {order.expected_delivery_date && (
        <div className="rounded-lg border border-emerald-200 bg-emerald-50 p-4">
          <div className="flex items-center gap-2">
            <Calendar className="h-5 w-5 text-emerald-600" />
            <div>
              <p className="text-xs font-semibold uppercase text-emerald-700">Expected Delivery</p>
              <p className="text-sm font-semibold text-emerald-800">
                {formatDeliveryDate(order.expected_delivery_date)}
              </p>
            </div>
          </div>
        </div>
      )}

      {/* Order Items with Images */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="mb-3 text-sm font-semibold text-slate-600">Order Items</h4>
        <div className="space-y-3">
          {order.items?.map((oi) => (
            <div key={oi.id} className="flex gap-3 rounded-lg border border-slate-100 p-3">
              {oi.item?.image_url ? (
                <img
                  src={oi.item.image_url}
                  alt={oi.item.name || `Item ${oi.item_id}`}
                  className="h-20 w-20 rounded-lg object-cover"
                />
              ) : (
                <div className="flex h-20 w-20 items-center justify-center rounded-lg bg-slate-100 text-slate-400">
                  No image
                </div>
              )}
              <div className="flex-1">
                <p className="font-medium text-slate-700">{oi.item?.name || `Item ${oi.item_id}`}</p>
                <p className="text-xs text-slate-500">{oi.item?.description || "No description"}</p>
                <div className="mt-2 flex items-center justify-between">
                  <div className="text-sm text-slate-600">
                    Qty: {oi.quantity} × ₹{oi.price_at_purchase?.toFixed(2) || "0.00"}
                  </div>
                  <div className="text-sm font-semibold text-slate-800">
                    ₹{((oi.price_at_purchase || 0) * (oi.quantity || 0)).toFixed(2)}
                  </div>
                </div>
                {oi.item?.discount_percent > 0 && (
                  <span className="mt-1 inline-block rounded-full bg-emerald-100 px-2 py-0.5 text-xs font-semibold text-emerald-700">
                    {oi.item.discount_percent}% off
                  </span>
                )}
              </div>
            </div>
          ))}
        </div>
      </div>

      {/* Bill Summary */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="mb-3 flex items-center gap-2 text-sm font-semibold text-slate-600">
          <IndianRupee className="h-4 w-4" />
          Bill Summary
        </h4>
        <div className="space-y-2 text-sm">
          <div className="flex justify-between">
            <span className="text-slate-600">Subtotal</span>
            <span className="text-slate-700">₹{subtotal.toFixed(2)}</span>
          </div>
          {totalDiscount > 0 && (
            <div className="flex justify-between">
              <span className="text-slate-600">Discount</span>
              <span className="text-emerald-600 font-medium">-₹{totalDiscount.toFixed(2)}</span>
            </div>
          )}
          <div className="flex justify-between">
            <span className="text-slate-600">CGST (9%)</span>
            <span className="text-slate-700">₹{cgst.toFixed(2)}</span>
          </div>
          <div className="flex justify-between">
            <span className="text-slate-600">SGST (9%)</span>
            <span className="text-slate-700">₹{sgst.toFixed(2)}</span>
          </div>
          <div className="border-t border-slate-200 pt-2">
            <div className="flex justify-between">
              <span className="font-semibold text-slate-800">Total Amount</span>
              <span className="text-lg font-bold text-slate-800">₹{finalTotal.toFixed(2)}</span>
            </div>
          </div>
        </div>
      </div>

      {/* Update Status */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="mb-3 text-sm font-semibold text-slate-600">Update Status</h4>
        <div className="flex flex-wrap gap-2">
          {statuses.map((status) => (
            <button
              key={status}
              onClick={() => onUpdateStatus(status)}
              disabled={loadingStatus}
              className={`rounded-full px-4 py-2 text-sm font-medium transition ${
                order.status === status || (typeof order.status === "object" && order.status?.value === status)
                  ? "bg-primary text-white"
                  : "border border-slate-200 bg-white text-slate-600 hover:bg-slate-100"
              }`}
            >
              {status.toUpperCase()}
            </button>
          ))}
        </div>
      </div>

      {/* Tracking Info */}
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h4 className="mb-3 text-sm font-semibold text-slate-600">Tracking Information</h4>
        {order.tracking_id && (
          <div className="mb-3 rounded-lg bg-slate-50 p-2 text-sm">
            <p className="text-slate-600">
              <span className="font-medium">Tracking ID:</span> {order.tracking_id}
            </p>
          </div>
        )}
        {order.tracking_url && (
          <a
            href={order.tracking_url}
            target="_blank"
            rel="noreferrer"
            className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white hover:bg-primary/90"
          >
            <MapPin className="h-4 w-4" />
            View on Google Maps
          </a>
        )}
      </div>
    </div>
  );
}

export default OrderStatusControls;
