import { cn } from "../utils/cn";

export default function Card({ className, children }) {
  return (
    <div className={cn("rounded-3xl border border-surface-variant/40 bg-surface-container-lowest p-6 shadow-soft dark:border-slate-700 dark:bg-slate-900", className)}>
      {children}
    </div>
  );
}