import { NavLink } from "react-router-dom";
import { cn } from "../utils/cn";
import { useI18n } from "../hooks/useI18n";

const navItems = [
  { to: "/", icon: "home", key: "home" },
  { to: "/workspace", icon: "content_paste_search", key: "detect" },
  { to: "/assistant", icon: "smart_toy", key: "assistant" },
];

export default function Sidebar({ showBrand = true }) {
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
                  ? "font-semibold text-[#183f26]"
                  : "text-emerald-800/80 hover:translate-x-1 hover:bg-white dark:text-emerald-100/80 dark:hover:bg-emerald-900/40"
              )
            }
          >
            <span className="material-symbols-outlined">{item.icon}</span>
            <span>{t.nav[item.key]}</span>
          </NavLink>
        ))}
      </nav>

    </aside>
  );
}