import { useI18n } from "../hooks/useI18n";

export default function ThemeToggle() {
  const { theme, toggleTheme, t } = useI18n();
  return (
    <button
      onClick={toggleTheme}
      className="rounded-full border border-outline-variant/70 bg-white/80 px-4 py-2 text-xs font-semibold text-on-surface transition hover:bg-primary hover:text-white dark:bg-slate-900 dark:text-slate-200"
    >
      {theme === "dark" ? "Light" : t.top.theme}
    </button>
  );
}