import { Menu, Bell } from "lucide-react";

function Topbar() {
  const appName = import.meta.env.VITE_APP_NAME || "Inventory Management";

  return (
    <header className="sticky top-0 z-10 flex items-center justify-between border-b border-slate-200 bg-white px-4 py-3 shadow-sm">
      <div className="flex items-center gap-3">
        <button className="rounded-lg border border-slate-200 p-2 lg:hidden">
          <Menu className="h-5 w-5" />
        </button>
        <div>
          <h1 className="text-lg font-semibold text-slate-800">{appName}</h1>
          <p className="text-xs text-slate-500">Manage inventory, orders, reports & taxes</p>
        </div>
      </div>
      <button className="relative rounded-full border border-slate-200 p-2 text-slate-500 hover:text-primary">
        <Bell className="h-5 w-5" />
        <span className="absolute -right-1 -top-1 h-2 w-2 rounded-full bg-primary"></span>
      </button>
    </header>
  );
}

export default Topbar;

