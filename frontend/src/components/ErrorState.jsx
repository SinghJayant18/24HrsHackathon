function ErrorState({ title = "Something went wrong", message, onRetry }) {
  return (
    <div className="rounded-xl border border-red-100 bg-red-50 p-6 text-red-600">
      <h3 className="text-lg font-semibold">{title}</h3>
      {message ? <p className="mt-2 text-sm text-red-500">{message}</p> : null}
      {onRetry ? (
        <button
          onClick={onRetry}
          className="mt-4 inline-flex items-center rounded-md bg-red-600 px-4 py-2 text-sm font-medium text-white shadow hover:bg-red-700"
        >
          Retry
        </button>
      ) : null}
    </div>
  );
}

export default ErrorState;

