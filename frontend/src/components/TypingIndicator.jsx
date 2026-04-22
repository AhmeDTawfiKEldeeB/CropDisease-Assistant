export default function TypingIndicator() {
  return (
    <div className="inline-flex items-center gap-1 rounded-full bg-surface-container-high px-3 py-2 dark:bg-slate-800">
      {[0, 1, 2].map((d) => (
        <span
          key={d}
          className="h-2 w-2 rounded-full bg-primary"
          style={{ animation: `typing 1.1s ${d * 0.14}s infinite` }}
        />
      ))}
    </div>
  );
}