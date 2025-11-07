import { useQuery } from "@tanstack/react-query";
import { fetchCatalogue } from "../api/catalogue.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import { ShoppingBag } from "lucide-react";

function Catalogue() {
  const catalogueQuery = useQuery({ queryKey: ["catalogue"], queryFn: fetchCatalogue });

  if (catalogueQuery.isLoading) {
    return <LoadingSpinner label="Loading catalogue..." />;
  }

  if (catalogueQuery.isError) {
    return <ErrorState message="Failed to load catalogue" onRetry={() => catalogueQuery.refetch()} />;
  }

  return (
    <div className="space-y-6">
      <div className="flex items-center justify-between">
        <div>
          <h2 className="text-2xl font-semibold text-slate-800">Catalogue</h2>
          <p className="text-sm text-slate-500">
            Public-facing view of inventory with pricing, discounts, and descriptions.
          </p>
        </div>
        <div className="flex items-center gap-2 rounded-lg bg-primary/10 px-3 py-2 text-sm text-primary">
          <ShoppingBag className="h-4 w-4" /> {catalogueQuery.data.length} items
        </div>
      </div>

      <div className="grid gap-6 md:grid-cols-2 xl:grid-cols-3">
        {catalogueQuery.data.map((item) => (
          <div key={item.id} className="rounded-xl border border-slate-200 bg-white shadow-sm transition hover:-translate-y-1 hover:shadow-md">
            {item.image_url ? (
              <img src={item.image_url} alt={item.name} className="h-40 w-full rounded-t-xl object-cover" />
            ) : (
              <div className="flex h-40 w-full items-center justify-center rounded-t-xl bg-slate-100 text-slate-400">
                No image
              </div>
            )}
            <div className="space-y-3 p-4">
              <div>
                <h3 className="text-lg font-semibold text-slate-800">{item.name}</h3>
                <p className="text-sm text-slate-500 line-clamp-3">
                  {item.description || "No description provided."}
                </p>
              </div>
              <div className="flex items-center justify-between">
                <p className="text-xl font-semibold text-slate-800">₹ {item.price}</p>
                <span className="rounded-full bg-emerald-100 px-3 py-1 text-xs font-semibold text-emerald-700">
                  {item.discount_percent}% off
                </span>
              </div>
              <p className="text-xs text-slate-500">
                Stock: {item.stock_quantity} • Updated {new Date(item.updated_at).toLocaleDateString()}
              </p>
            </div>
          </div>
        ))}
        {catalogueQuery.data.length === 0 ? (
          <div className="rounded-xl border border-slate-200 bg-white p-6 text-sm text-slate-500">
            No catalogue items available. Add active inventory items to publish them here.
          </div>
        ) : null}
      </div>
    </div>
  );
}

export default Catalogue;

