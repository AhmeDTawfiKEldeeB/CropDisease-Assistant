import { NavLink } from "react-router-dom";
import { cn } from "../utils/cn";
import { useI18n } from "../hooks/useI18n";

const navItems = [
  { to: "/", icon: "home", key: "home" },
  { to: "/workspace", icon: "content_paste_search", key: "detect" },
  { to: "/assistant", icon: "smart_toy", key: "assistant" },
  { to: "/history", icon: "history", key: "history" },
  { to: "/settings", icon: "settings", key: "settings" },
];

export default function Sidebar({ showBrand = true, showUpgrade = true }) {
  const { t } = useI18n();

  return (
    <aside className="hidden h-screen w-72 flex-col rounded-r-[2rem] border-r border-emerald-100/50 bg-emerald-50/80 p-6 shadow-soft lg:flex dark:border-slate-700 dark:bg-slate-900/80">
      {showBrand ? (
        <div className="mb-5">
          <h2 className="text-2xl font-black tracking-tight text-emerald-900 dark:text-emerald-200">{t.appName}</h2>
          <p className="text-xs font-semibold uppercase tracking-wider text-emerald-700/70">Premium Plan</p>
        </div>
      ) : null}

      <nav className="space-y-2">
        {navItems.map((item) => (
          <NavLink
            key={item.to}
            to={item.to}
            className={({ isActive }) =>
              cn(
                "flex items-center gap-3 rounded-full px-4 py-3 text-sm font-medium transition-all",
                isActive
                  ? "bg-emerald-600 text-white shadow-lg shadow-emerald-200/60 dark:shadow-none"
                  : "text-emerald-800/80 hover:translate-x-1 hover:bg-emerald-100 dark:text-emerald-100/80 dark:hover:bg-emerald-900/40"
              )
            }
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span>{t.nav[item.key]}</span>
          </NavLink>
        ))}
      </nav>

      <div className="mt-auto space-y-4 border-t border-emerald-100/70 pt-6 dark:border-slate-700">
        {showUpgrade ? (
          <div className="rounded-2xl border border-primary/20 bg-primary/10 p-4">
            <p className="mb-2 text-xs font-bold text-primary">{t.nav.upgrade}</p>
            <div className="h-1.5 w-full overflow-hidden rounded-full bg-primary/20">
              <div className="h-full w-2/3 rounded-full bg-primary" />
            </div>
          </div>
        ) : null}
        <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-emerald-800/80 transition hover:bg-emerald-100 dark:text-emerald-100/80 dark:hover:bg-emerald-900/40">
          <span className="material-symbols-outlined">help</span>
          {t.nav.help}
        </button>
        <button className="flex w-full items-center gap-3 rounded-xl px-3 py-2 text-sm text-emerald-800/80 transition hover:bg-emerald-100 dark:text-emerald-100/80 dark:hover:bg-emerald-900/40">
          <span className="material-symbols-outlined">logout</span>
          {t.nav.signOut}
        </button>
      </div>
    </aside>
  );
}