import Sidebar from "./Sidebar";
import TopControls from "./TopControls";

export default function Layout({ title, subtitle, children, sidebarOptions }) {
  return (
    <div className="flex min-h-screen bg-surface text-on-surface dark:bg-slate-950 dark:text-slate-100">
      <Sidebar {...sidebarOptions} />
      <div className="flex-1">
        <header className="sticky top-0 z-30 flex items-center justify-between border-b border-surface-variant/50 bg-surface/80 px-5 py-4 backdrop-blur-xl md:px-8 dark:border-slate-800 dark:bg-slate-950/80">
          <div>
            <h1 className="text-2xl font-black tracking-tight md:text-4xl">{title}</h1>
            {subtitle ? <p className="mt-1 max-w-2xl text-sm text-on-surface-variant dark:text-slate-400">{subtitle}</p> : null}
          </div>
          <TopControls />
        </header>
        <main className="p-4 md:p-8">{children}</main>
      </div>
    </div>
  );
}