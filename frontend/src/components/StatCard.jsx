function StatCard({ title, value, icon: Icon, description }) {
  return (
    <div className="rounded-xl border border-slate-200 bg-white p-4 shadow-sm">
      <div className="flex items-center justify-between">
        <div>
          <p className="text-sm uppercase tracking-wide text-slate-500">
            {title}
          </p>
          <p className="mt-2 text-2xl font-semibold text-slate-800">{value}</p>
        </div>
        {Icon ? <Icon className="h-10 w-10 text-primary" /> : null}
      </div>
      {description ? (
        <p className="mt-2 text-xs text-slate-500">{description}</p>
      ) : null}
    </div>
  );
}

export default StatCard;

