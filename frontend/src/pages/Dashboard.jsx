import { useQuery } from "@tanstack/react-query";
import { fetchItems } from "../api/items.js";
import { fetchCatalogue } from "../api/catalogue.js";
import { fetchTaxSummary } from "../api/reports.js";
import LoadingSpinner from "../components/LoadingSpinner.jsx";
import ErrorState from "../components/ErrorState.jsx";
import StatCard from "../components/StatCard.jsx";
import { Package, ShoppingCart, IndianRupee, Calendar } from "lucide-react";
import { format } from "date-fns";

function Dashboard() {
  const itemsQuery = useQuery({ queryKey: ["items"], queryFn: fetchItems });
  const catalogueQuery = useQuery({ queryKey: ["catalogue"], queryFn: fetchCatalogue });
  const taxQuery = useQuery({
    queryKey: ["tax-summary", "month"],
    queryFn: () =>
      fetchTaxSummary({ period: "month", date_ref: format(new Date(), "yyyy-MM-01") })
  });

  if (itemsQuery.isLoading || catalogueQuery.isLoading || taxQuery.isLoading) {
    return <LoadingSpinner label="Loading dashboard..." />;
  }

  if (itemsQuery.isError || catalogueQuery.isError || taxQuery.isError) {
    return (
      <ErrorState
        message="Unable to load dashboard data"
        onRetry={() => {
          itemsQuery.refetch();
          catalogueQuery.refetch();
          taxQuery.refetch();
        }}
      />
    );
  }

  const activeItems = itemsQuery.data.filter((item) => item.is_active);
  const outOfStock = itemsQuery.data.filter((item) => item.stock_quantity <= 0);

  return (
    <div className="space-y-6">
      <div>
        <h2 className="text-2xl font-semibold text-slate-800">Overview</h2>
        <p className="text-sm text-slate-500">
          Quick snapshot of inventory health and revenue performance
        </p>
      </div>

      <div className="grid gap-4 md:grid-cols-2 xl:grid-cols-4">
        <StatCard
          title="Active Items"
          value={activeItems.length}
          icon={Package}
          description={`${outOfStock.length} items currently out of stock`}
        />
        <StatCard
          title="Catalogue Items"
          value={catalogueQuery.data.length}
          icon={ShoppingCart}
          description="Total products visible to customers"
        />
        <StatCard
          title="Monthly Revenue"
          value={`₹ ${taxQuery.data.total_revenue.toFixed(2)}`}
          icon={IndianRupee}
          description={`Estimated tax due: ₹ ${taxQuery.data.total_tax_due.toFixed(2)}`}
        />
        <StatCard
          title="Tax Period"
          value={taxQuery.data.period}
          icon={Calendar}
          description={`${taxQuery.data.tax_rate_percent}% tax rate applied`}
        />
      </div>

      <div className="grid gap-4 lg:grid-cols-2">
        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800">Low Stock Alerts</h3>
          <p className="text-sm text-slate-500">Items below desired inventory levels</p>
          <div className="mt-4 space-y-3">
            {itemsQuery.data
              .filter((item) => item.stock_quantity <= 5)
              .map((item) => (
                <div
                  key={item.id}
                  className="flex items-center justify-between rounded-lg border border-amber-100 bg-amber-50 p-3 text-sm"
                >
                  <div>
                    <p className="font-medium text-amber-700">{item.name}</p>
                    <p className="text-xs text-amber-600">
                      Stock: {item.stock_quantity} • Price: ₹ {item.price}
                    </p>
                  </div>
                  <span className="rounded-full bg-amber-100 px-3 py-1 text-xs font-semibold text-amber-700">
                    Restock
                  </span>
                </div>
              ))}
            {itemsQuery.data.filter((item) => item.stock_quantity <= 5).length === 0 ? (
              <p className="text-sm text-slate-500">All items are sufficiently stocked.</p>
            ) : null}
          </div>
        </div>

        <div className="rounded-xl border border-slate-200 bg-white p-6 shadow-sm">
          <h3 className="text-lg font-semibold text-slate-800">Recent Catalogue Entries</h3>
          <p className="text-sm text-slate-500">Latest products available for customers</p>
          <div className="mt-4 space-y-4">
            {catalogueQuery.data.slice(0, 5).map((item) => (
              <div key={item.id} className="flex gap-3 rounded-lg border border-slate-100 p-3">
                {item.image_url ? (
                  <img
                    src={item.image_url}
                    alt={item.name}
                    className="h-16 w-16 rounded-lg object-cover"
                  />
                ) : (
                  <div className="flex h-16 w-16 items-center justify-center rounded-lg bg-slate-100 text-slate-400">
                    No image
                  </div>
                )}
                <div>
                  <p className="font-medium text-slate-700">{item.name}</p>
                  <p className="text-xs text-slate-500">₹ {item.price} • {item.discount_percent}% off</p>
                  <p className="mt-1 text-xs text-slate-500 line-clamp-2">
                    {item.description || "No description"}
                  </p>
                </div>
              </div>
            ))}
            {catalogueQuery.data.length === 0 ? (
              <p className="text-sm text-slate-500">No catalogue items yet.</p>
            ) : null}
          </div>
        </div>
      </div>
    </div>
  );
}

export default Dashboard;

