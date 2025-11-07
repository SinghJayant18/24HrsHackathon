import { useFieldArray, useForm } from "react-hook-form";

function OrderCreateForm({ itemsOptions, onSubmit, submitting }) {
  const {
    control,
    register,
    handleSubmit,
    reset,
    formState: { errors }
  } = useForm({
    defaultValues: {
      customer: {
        name: "",
        email: "",
        address: "",
        phone: ""
      },
      items: [
        {
          item_id: "",
          quantity: 1
        }
      ]
    }
  });

  const { fields, append, remove } = useFieldArray({ control, name: "items" });

  const handleCreate = (values) => {
    const payload = {
      customer: values.customer,
      items: values.items.map((it) => ({
        item_id: Number(it.item_id),
        quantity: Number(it.quantity)
      }))
    };
    onSubmit(payload, () => reset());
  };

  return (
    <form onSubmit={handleSubmit(handleCreate)} className="grid gap-4">
      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <h3 className="text-sm font-semibold text-slate-600">Customer Details</h3>
        <div className="mt-3 grid gap-3 sm:grid-cols-2">
          <div className="grid gap-1">
            <label className="text-xs uppercase text-slate-500">Name *</label>
            <input
              {...register("customer.name", { required: "Name required" })}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            {errors.customer?.name ? (
              <span className="text-xs text-red-500">
                {errors.customer.name.message}
              </span>
            ) : null}
          </div>
          <div className="grid gap-1">
            <label className="text-xs uppercase text-slate-500">Email *</label>
            <input
              type="email"
              {...register("customer.email", { required: "Email required" })}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
            {errors.customer?.email ? (
              <span className="text-xs text-red-500">
                {errors.customer.email.message}
              </span>
            ) : null}
          </div>
          <div className="grid gap-1">
            <label className="text-xs uppercase text-slate-500">Phone</label>
            <input
              {...register("customer.phone")}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
          </div>
          <div className="grid gap-1 sm:col-span-2">
            <label className="text-xs uppercase text-slate-500">Address</label>
            <textarea
              {...register("customer.address")}
              rows={2}
              className="rounded-lg border border-slate-200 px-3 py-2 text-sm"
            />
          </div>
        </div>
      </div>

      <div className="rounded-lg border border-slate-200 bg-white p-4 shadow-sm">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-semibold text-slate-600">Items *</h3>
          <button
            type="button"
            onClick={() => append({ item_id: "", quantity: 1 })}
            className="text-sm font-medium text-primary hover:underline"
          >
            + Add item
          </button>
        </div>
        <div className="mt-3 space-y-3">
          {fields.map((field, idx) => (
            <div key={field.id} className="grid gap-3 rounded-lg border border-slate-100 p-3 sm:grid-cols-5">
              <div className="sm:col-span-3">
                <label className="text-xs uppercase text-slate-500">Item</label>
                <select
                  {...register(`items.${idx}.item_id`, { required: "Select item" })}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                >
                  <option value="">Select...</option>
                  {itemsOptions.map((item) => (
                    <option key={item.id} value={item.id}>
                      {item.name} (₹{item.price})
                    </option>
                  ))}
                </select>
                {errors.items?.[idx]?.item_id ? (
                  <span className="text-xs text-red-500">
                    {errors.items[idx].item_id.message}
                  </span>
                ) : null}
              </div>
              <div>
                <label className="text-xs uppercase text-slate-500">Quantity</label>
                <input
                  type="number"
                  min={1}
                  {...register(`items.${idx}.quantity`, { required: "Qty" })}
                  className="mt-1 w-full rounded-lg border border-slate-200 px-3 py-2 text-sm"
                />
              </div>
              <div className="flex items-end">
                <button
                  type="button"
                  onClick={() => remove(idx)}
                  className="w-full rounded-lg border border-red-200 px-3 py-2 text-sm font-medium text-red-500 hover:bg-red-50"
                  disabled={fields.length === 1}
                >
                  Remove
                </button>
              </div>
            </div>
          ))}
        </div>
      </div>

      <div className="flex justify-end">
        <button
          type="submit"
          disabled={submitting}
          className="rounded-lg bg-primary px-4 py-2 text-sm font-semibold text-white shadow hover:bg-primary/90 disabled:opacity-60"
        >
          {submitting ? "Placing..." : "Place Order"}
        </button>
      </div>
    </form>
  );
}

export default OrderCreateForm;

