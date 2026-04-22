export default function ProgressBar({ value = 50, animated = false }) {
  return (
    <div className="h-3 w-full overflow-hidden rounded-full bg-surface-container-high dark:bg-slate-800">
      <div
        className={animated ? "h-full rounded-full bg-gradient-to-r from-primary to-primary-container animate-pulsebar" : "h-full rounded-full bg-gradient-to-r from-primary to-primary-container"}
        style={!animated ? { width: `${value}%` } : undefined}
      />
    </div>
  );
}