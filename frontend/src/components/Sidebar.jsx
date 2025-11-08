import { NavLink } from "react-router-dom";
import {
  LayoutDashboard,
  Package2,
  ClipboardList,
  FileBarChart,
  Calculator,
  ShoppingBag
} from "lucide-react";

const navigation = [
  { to: "/dashboard", label: "Dashboard", icon: LayoutDashboard },
  { to: "/items", label: "Inventory", icon: Package2 },
  { to: "/orders", label: "Orders", icon: ClipboardList },
  { to: "/reports", label: "Reports", icon: FileBarChart },
  { to: "/taxes", label: "Taxes", icon: Calculator },
  { to: "/catalogue", label: "Catalogue", icon: ShoppingBag }
];

function Sidebar() {
  return (
    <aside className="hidden w-64 flex-col border-r border-slate-200 bg-white p-4 shadow-sm lg:flex">
      <div className="mb-10 flex items-center gap-2 text-xl font-semibold text-primary">
        <Package2 className="h-6 w-6" />
        <span>Small Scale Business Automation</span>
      </div>
      <nav className="flex flex-1 flex-col gap-2">
        {navigation.map((item) => {
          const Icon = item.icon;
          return (
            <NavLink
              key={item.to}
              to={item.to}
              className={({ isActive }) =>
                `flex items-center gap-3 rounded-lg px-3 py-2 text-sm font-medium transition hover:bg-slate-100 ${
                  isActive ? "bg-primary/10 text-primary" : "text-slate-600"
                }`
              }
            >
              <Icon className="h-5 w-5" />
              {item.label}
            </NavLink>
          );
        })}
      </nav>
      <div className="mt-auto rounded-lg bg-slate-50 p-3 text-xs text-slate-500">
        Backend API: <span className="font-semibold">{import.meta.env.VITE_API_BASE_URL || "http://localhost:8000"}</span>
      </div>
    </aside>
  );
}

export default Sidebar;

