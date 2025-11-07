import { useMutation, useQuery, useQueryClient } from "@tanstack/react-query";
import { useState } from "react";
import {
  fetchItems,
  createItem,
  updateItem,
  fetchItemById
} from "../api/items.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import ItemForm from "../components/ItemForm.jsx";
import { Pencil, Plus, RefreshCw, Search } from "lucide-react";

function Items() {
  const queryClient = useQueryClient();
  const [selectedItem, setSelectedItem] = useState(null);
  const [searchId, setSearchId] = useState("");
  const itemsQuery = useQuery({ queryKey: ["items"], queryFn: fetchItems });

  const createMutation = useMutation({
    mutationFn: createItem,
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
      setSelectedItem(null);
      alert("Item created successfully");
    },
    onError: (err) => alert(err.response?.data?.detail || "Failed to create item")
  });

  const updateMutation = useMutation({
    mutationFn: ({ id, payload }) => updateItem({ id, payload }),
    onSuccess: () => {
      queryClient.invalidateQueries({ queryKey: ["items"] });
      setSelectedItem(null);
      alert("Item updated successfully");
    },
    onError: (err) => alert(err.response?.data?.detail || "Failed to update item")
  });

  const findItem = async () => {
    if (!searchId) return;
    try {
      const item = await fetchItemById(searchId);
      setSelectedItem(item);
      alert("Item loaded. Scroll to the form to edit.");
    } catch (error) {
      alert("Item not found");
    }
  };

  if (itemsQuery.isLoading) {
    return <LoadingSpinner label="Loading items..." />;
  }

  if (itemsQuery.isError) {
    return (
      <ErrorState
        message="Unable to fetch items"
        onRetry={() => itemsQuery.refetch()}
      />
    );
  }

  const handleSubmit = (payload, onSuccess) => {
    if (selectedItem) {
      updateMutation.mutate({ id: selectedItem.id, payload });
    } else {
      createMutation.mutate(payload);
    }
    if (onSuccess) onSuccess();
  };

  return (
    <div className="space-y-6">
      <div className="flex flex-wrap items-center justify-between gap-4">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Inventory</h2>
          <p className="text-sm text-slate-500">
            Manage catalogue items, pricing, discounts, and stock levels
          </p>
        </div>
        <button
          onClick={() => setSelectedItem(null)}
          className="inline-flex items-center gap-2 rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary/90"
        >
          <Plus className="h-4 w-4" /> New Item
        </button>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex flex-col gap-4 lg:flex-row lg:items-center lg:justify-between">
          <div>
            <h3 className="text-lg font-semibold text-slate-800">Inventory List</h3>
            <p className="text-sm text-slate-500">
              Track stock availability, discounts, and active catalogue items
            </p>
          </div>
          <div className="flex items-center gap-2">
            <div className="flex items-center rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600">
              <Search className="mr-2 h-4 w-4 text-slate-400" />
              <input
                placeholder="Quick fetch by ID"
                value={searchId}
                onChange={(e) => setSearchId(e.target.value)}
                className="w-32 border-none bg-transparent outline-none"
              />
            </div>
            <button
              onClick={findItem}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm font-medium text-slate-600 hover:bg-slate-100"
            >
              Load Item
            </button>
            <button
              onClick={() => itemsQuery.refetch()}
              className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-2 text-sm text-slate-600 hover:bg-slate-100"
            >
              <RefreshCw className="h-4 w-4" /> Refresh
            </button>
          </div>
        </div>

        <div className="mt-4 overflow-x-auto">
          <table className="min-w-full divide-y divide-slate-200 text-left text-sm">
            <thead className="bg-slate-50 text-xs uppercase text-slate-500">
              <tr>
                <th className="px-4 py-3">ID</th>
                <th className="px-4 py-3">Name</th>
                <th className="px-4 py-3">Price</th>
                <th className="px-4 py-3">Discount %</th>
                <th className="px-4 py-3">Stock</th>
                <th className="px-4 py-3">Active</th>
                <th className="px-4 py-3">Actions</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-200">
              {itemsQuery.data.map((item) => (
                <tr key={item.id} className="hover:bg-slate-50">
                  <td className="px-4 py-3 font-medium text-slate-600">{item.id}</td>
                  <td className="px-4 py-3 text-slate-700">{item.name}</td>
                  <td className="px-4 py-3">₹ {item.price}</td>
                  <td className="px-4 py-3">{item.discount_percent}%</td>
                  <td className={`px-4 py-3 ${item.stock_quantity <= 0 ? "text-red-500" : "text-slate-700"}`}>
                    {item.stock_quantity}
                  </td>
                  <td className="px-4 py-3">
                    <span className={`rounded-full px-3 py-1 text-xs font-semibold ${
                      item.is_active
                        ? "bg-emerald-100 text-emerald-700"
                        : "bg-slate-200 text-slate-500"
                    }`}>
                      {item.is_active ? "Active" : "Disabled"}
                    </span>
                  </td>
                  <td className="px-4 py-3">
                    <button
                      onClick={() => setSelectedItem(item)}
                      className="inline-flex items-center gap-2 rounded-lg border border-slate-200 px-3 py-1 text-xs font-medium text-slate-600 hover:bg-slate-100"
                    >
                      <Pencil className="h-3 w-3" /> Edit
                    </button>
                  </td>
                </tr>
              ))}
              {itemsQuery.data.length === 0 ? (
                <tr>
                  <td colSpan={7} className="px-4 py-6 text-center text-sm text-slate-500">
                    No items found. Create your first item using the form below.
                  </td>
                </tr>
              ) : null}
            </tbody>
          </table>
        </div>
      </div>

      <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
        <div className="mb-4 flex items-center justify-between">
          <h3 className="text-lg font-semibold text-slate-800">
            {selectedItem ? `Edit Item #${selectedItem.id}` : "Create New Item"}
          </h3>
          {selectedItem ? (
            <button
              onClick={() => setSelectedItem(null)}
              className="text-sm font-medium text-primary hover:underline"
            >
              + New item instead
            </button>
          ) : null}
        </div>
        <ItemForm
          initialValues={selectedItem}
          onSubmit={handleSubmit}
          submitting={createMutation.isLoading || updateMutation.isLoading}
        />
      </div>
    </div>
  );
}

export default Items;

