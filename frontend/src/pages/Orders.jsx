import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import { fetchItems } from "../api/items.js";
import {
  createOrder,
  getOrder,
  updateOrderStatus,
  assignTracking,
  fetchOrders
} from "../api/orders.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import OrderCreateForm from "../components/OrderCreateForm.jsx";
import OrderStatusControls from "../components/OrderStatusControls.jsx";
import { OrderStatusBadge } from "../components/OrderStatusBadge.jsx";
import { Search, Truck, RefreshCw } from "lucide-react";

function Orders() {
  const queryClient = useQueryClient();
  const [orderIdInput, setOrderIdInput] = useState("");
  const [currentOrder, setCurrentOrder] = useState(null);

  const itemsQuery = useQuery({ queryKey: ["items"], queryFn: fetchItems });
  const ordersQuery = useQuery({ queryKey: ["orders"], queryFn: fetchOrders });

  const createMutation = useMutation({
    mutationFn: createOrder,
    onSuccess: (data) => {
      setCurrentOrder(data);
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      alert(`Order #${data.id} created. Customer will receive email notifications.`);
    },
    onError: (err) => alert(err.response?.data?.detail || "Failed to create order")
  });

  const fetchOrderMutation = useMutation({
    mutationFn: getOrder,
    onSuccess: (data) => setCurrentOrder(data),
    onError: () => alert("Order not found")
  });

  const updateStatusMutation = useMutation({
    mutationFn: ({ id, status }) => updateOrderStatus({ id, status }),
    onSuccess: (data) => {
      setCurrentOrder(data);
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      alert("Order status updated.");
    },
    onError: () => alert("Failed to update status")
  });

  const trackingMutation = useMutation({
    mutationFn: ({ id, tracking_id, lat, lng }) => assignTracking({ id, tracking_id, lat, lng }),
    onSuccess: (data) => {
      setCurrentOrder((prev) => ({ ...prev, tracking_id: data.tracking_id, tracking_url: data.tracking_url }));
      queryClient.invalidateQueries({ queryKey: ["orders"] });
      alert("Tracking saved.");
    },
    onError: () => alert("Failed to save tracking")
  });

  if (itemsQuery.isLoading || ordersQuery.isLoading) {
    return <LoadingSpinner label="Loading orders workspace..." />;
  }

  if (itemsQuery.isError || ordersQuery.isError) {
    return (
      <ErrorState
        message="Unable to load orders workspace"
        onRetry={() => {
          itemsQuery.refetch();
          ordersQuery.refetch();
        }}
      />
    );
  }

  const handleStatusUpdate = (status) => {
    if (!currentOrder) return;
    updateStatusMutation.mutate({ id: currentOrder.id, status });
  };

  const handleAssignTracking = ({ trackingId, lat, lng }) => {
    if (!currentOrder) return;
    trackingMutation.mutate({
      id: currentOrder.id,
      tracking_id: trackingId,
      lat: lat || undefined,
      lng: lng || undefined
    });
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Orders</h2>
          <p className="text-sm text-slate-500">
            Create orders, update their statuses, and manage shipping tracking links
          </p>
        </div>
        <div className="flex items-center gap-2">
          <div className="flex items-center rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600">
            <Search className="mr-2 h-4 w-4 text-slate-400" />
            <input
              placeholder="Order ID"
              value={orderIdInput}
              onChange={(e) => setOrderIdInput(e.target.value)}
              className="w-24 border-none bg-transparent outline-none"
            />
          </div>
          <button
            onClick={() => orderIdInput && fetchOrderMutation.mutate(orderIdInput)}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
          >
            Fetch Order
          </button>
        </div>
      </div>

      <div className="grid gap-6 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <div className="mb-4 flex items-center gap-3">
            <div className="rounded-full bg-primary/10 p-3 text-primary">
              <Truck className="h-5 w-5" />
            </div>
            <div>
              <h3 className="text-lg font-semibold text-slate-800">Create New Order</h3>
              <p className="text-sm text-slate-500">
                Customer and order items will trigger email notifications to both parties.
              </p>
            </div>
          </div>
          <OrderCreateForm
            itemsOptions={itemsQuery.data}
            onSubmit={(payload) => createMutation.mutate(payload)}
            submitting={createMutation.isLoading}
          />
        </div>

        <div className="space-y-4">
          <OrderStatusControls
            order={currentOrder}
            onUpdateStatus={handleStatusUpdate}
            onAssignTracking={handleAssignTracking}
            loadingStatus={updateStatusMutation.isLoading}
            loadingTracking={trackingMutation.isLoading}
          />
          {!currentOrder ? (
            <div className="rounded-lg border border-slate-200 bg-slate-50 p-6 text-sm text-slate-500">
              Fetch an existing order or create a new one to manage status, tracking, and notifications.
            </div>
          ) : null}
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex flex-wrap items-center justify-between gap-3">
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Recent Orders</h3>
            <p className="text-sm text-slate-500">Click manage to view or update order details.</p>
          </div>
          <button
            onClick={() => ordersQuery.refetch()}
            className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
          >
            <RefreshCw className="h-4 w-4" /> Refresh
          </button>
        </div>
        <div className="overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">Order</th>
                <th className="px-4 py-3">Customer</th>
                <th className="px-4 py-3">Total</th>
                <th className="px-4 py-3">Items</th>
                <th className="px-4 py-3">Status</th>
                <th className="px-4 py-3">Placed</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-100">
              {ordersQuery.data.map((order) => (
                <tr key={order.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-700">#{order.id}</td>
                  <td className="px-4 py-3">
                    <p className="text-sm text-slate-700">{order.customer?.name}</p>
                    <p className="text-xs text-slate-500">{order.customer?.email}</p>
                  </td>
                  <td className="px-4 py-3 text-slate-700">₹ {order.total_amount?.toFixed(2)}</td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {order.items.map((item) => (
                      <span key={item.id} className="mr-2 inline-block rounded-full bg-slate-100 px-2 py-1">
                        {item.item?.name || `Item ${item.item_id}`} × {item.quantity}
                      </span>
                    ))}
                  </td>
                  <td className="px-4 py-3">
                    <OrderStatusBadge status={order.status} />
                  </td>
                  <td className="px-4 py-3 text-xs text-slate-500">
                    {new Date(order.created_at).toLocaleString()}
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setCurrentOrder(order)}
                      className="rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                    >
                      Manage
                    </button>
                  </td>
                </tr>
              ))}
              {ordersQuery.data.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-center text-sm text-slate-500">
                    No orders yet. Create one using the form above.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
}

export default Orders;

