import { useForm } from "react-hook-form";

const defaultValues = {
  name: "",
  description: "",
  price: "",
  discount_percent: 0,
  image_url: "",
  stock_quantity: 0,
  is_active: true
};

function ItemForm({ initialValues, onSubmit, submitting }) {
  const {
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm({ defaultValues: initialValues || defaultValues });

  const submitHandler = (values) => {
    // Coerce numeric fields
    const payload = {
      ...values,
      price: Number(values.price),
      discount_percent: Number(values.discount_percent || 0),
      stock_quantity: Number(values.stock_quantity || 0)
    };
    onSubmit(payload, () => reset(defaultValues));
  };

  return (
    <form onSubmit={handleSubmit(submitHandler)} className="grid gap-4">
      <div className="grid gap-1">
        <label className="text-sm font-medium text-slate-600">Name *</label>
        <input
          {...register("name", { required: "Name is required" })}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
          placeholder="Item name"
        />
        {errors.name ? (
          <span className="text-xs text-red-500">{errors.name.message}</span>
        ) : null}
      </div>

      <div className="grid gap-1">
        <label className="text-sm font-medium text-slate-600">Description</label>
        <textarea
          {...register("description")}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
          rows={3}
          placeholder="Short description"
        />
      </div>

      <div className="grid gap-3 sm:grid-cols-3">
        <div className="grid gap-1">
          <label className="text-sm font-medium text-slate-600">Price *</label>
          <input
            type="number"
            step="0.01"
            {...register("price", { required: "Price is required" })}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            placeholder="0.00"
          />
          {errors.price ? (
            <span className="text-xs text-red-500">{errors.price.message}</span>
          ) : null}
        </div>

        <div className="grid gap-1">
          <label className="text-sm font-medium text-slate-600">Discount %</label>
          <input
            type="number"
            step="0.01"
            {...register("discount_percent")}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            placeholder="0"
          />
        </div>

        <div className="grid gap-1">
          <label className="text-sm font-medium text-slate-600">Stock *</label>
          <input
            type="number"
            {...register("stock_quantity", { required: "Stock is required" })}
            className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            placeholder="0"
          />
          {errors.stock_quantity ? (
            <span className="text-xs text-red-500">{errors.stock_quantity.message}</span>
          ) : null}
        </div>
      </div>

      <div className="grid gap-1">
        <label className="text-sm font-medium text-slate-600">Image URL</label>
        <input
          {...register("image_url")}
          className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
          placeholder="https://..."
        />
      </div>

      <label className="flex items-center gap-2 text-sm text-slate-600">
        <input type="checkbox" {...register("is_active")} /> Active item
      </label>

      <div className="flex justify-end gap-3">
        <button
          type="button"
          onClick={() => reset(defaultValues)}
          className="rounded-lg border border-slate-200 px-4 py-2 text-sm font-medium text-slate-600 hover:bg-slate-50"
        >
          Reset
        </button>
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary/90 disabled:opacity-60"
        >
          {submitting ? "Saving..." : "Save Item"}
        </button>
      </div>
    </form>
  );
}

export default ItemForm;

