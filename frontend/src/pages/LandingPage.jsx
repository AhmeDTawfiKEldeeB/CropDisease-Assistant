import { Link } from "react-router-dom";
import PageTransition from "../components/PageTransition";
import TopControls from "../components/TopControls";
import { imageUrls } from "../data/mockData";
import { useI18n } from "../hooks/useI18n";

export default function LandingPage() {
  const { t, isRTL } = useI18n();

  return (
    <PageTransition>
      <div className="min-h-screen bg-surface text-on-surface dark:bg-slate-950 dark:text-slate-100">
        <nav className="fixed top-0 z-50 w-full border-b border-emerald-100/60 bg-emerald-50/80 px-4 py-3 backdrop-blur-xl md:px-8 dark:border-slate-800 dark:bg-slate-900/80">
          <div className="mx-auto flex max-w-7xl items-center justify-between">
            <div className="text-xl font-black tracking-tight text-emerald-900 dark:text-emerald-100">{t.appName}</div>
            <div className="hidden items-center gap-8 text-sm md:flex">
              <a href="#" className="border-b-2 border-emerald-600 pb-1 font-semibold text-emerald-700">
                Science
              </a>
              <a href="#" className="text-slate-600 transition hover:text-emerald-800 dark:text-slate-300">
                Solutions
              </a>
              <a href="#" className="text-slate-600 transition hover:text-emerald-800 dark:text-slate-300">
                Pricing
              </a>
              <a href="#" className="text-slate-600 transition hover:text-emerald-800 dark:text-slate-300">
                About
              </a>
            </div>
            <TopControls />
          </div>
        </nav>

        <section className="relative overflow-hidden px-6 pb-16 pt-24 lg:px-12">
          <div className="absolute inset-0 bg-gradient-to-br from-emerald-50 via-surface to-white dark:from-slate-950 dark:via-slate-950 dark:to-slate-900" />
          <div className="absolute -left-14 top-20 h-[420px] w-[420px] rounded-full bg-primary/10 blur-3xl" />
          <div className="absolute -bottom-10 right-0 h-[300px] w-[300px] rounded-full bg-tertiary/10 blur-3xl" />

          <div className="relative mx-auto grid min-h-[88vh] max-w-7xl grid-cols-1 items-center gap-12 lg:grid-cols-2">
            <div className="space-y-8">
              <div className="inline-flex items-center gap-2 rounded-full bg-primary-fixed px-4 py-2 text-xs font-bold uppercase tracking-wider text-on-primary-fixed">
                <span className="material-symbols-outlined text-sm">auto_awesome</span>
                {t.landing.badge}
              </div>

              <h1 className="text-5xl font-black leading-[1.1] tracking-tight lg:text-7xl">
                {t.landing.titleA} <br />
                <span className="italic text-primary">{t.landing.titleB}</span>
              </h1>
              <p className="max-w-2xl text-lg leading-8 text-on-surface-variant">{t.landing.subtitle}</p>

              <div className="flex flex-col gap-4 sm:flex-row">
                <Link
                  to="/workspace"
                  className="flex items-center justify-center gap-2 rounded-2xl bg-gradient-to-r from-primary to-primary-container px-8 py-4 text-lg font-bold text-white shadow-xl transition hover:scale-[1.02]"
                >
                  <span className="material-symbols-outlined">upload_file</span>
                  {t.landing.ctaUpload}
                </Link>
                <button className="rounded-2xl px-8 py-4 font-semibold transition hover:bg-surface-container dark:hover:bg-slate-800">
                  {t.landing.ctaDemo}
                </button>
              </div>

              <div className="flex items-center gap-4 border-t border-outline-variant/30 pt-6">
                <div className={isRTL ? "flex space-x-reverse -space-x-3" : "flex -space-x-3"}>
                  {[1, 2, 3].map((item) => (
                    <img
                      key={item}
                      src={`https://i.pravatar.cc/100?img=${item + 10}`}
                      className="h-12 w-12 rounded-full border-4 border-surface object-cover"
                      alt="avatar"
                    />
                  ))}
                </div>
                <div>
                  <p className="font-bold">{t.landing.trusted}</p>
                  <p className="text-sm text-on-surface-variant">{t.landing.trustedSub}</p>
                </div>
              </div>
            </div>

            <div className="relative">
              <div className="relative overflow-hidden rounded-3xl bg-surface-container-high shadow-2xl">
                <img src={imageUrls.hero} alt="hero" className="aspect-[4/5] w-full object-cover" />

                <div className={isRTL ? "glass absolute right-6 top-8 w-64 animate-float rounded-2xl border-r-4 border-primary p-4 shadow-2xl" : "glass absolute left-6 top-8 w-64 animate-float rounded-2xl border-l-4 border-primary p-4 shadow-2xl"}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="rounded-full bg-primary-fixed px-2 py-1 text-[10px] font-bold">HEALTHY</span>
                    <span className="material-symbols-outlined text-primary">check_circle</span>
                  </div>
                  <p className="font-bold">Monstera Deliciosa</p>
                  <p className="text-xs text-on-surface-variant">Chlorophyll efficiency at 98%.</p>
                </div>

                <div className={isRTL ? "glass absolute bottom-12 left-6 w-72 animate-float rounded-2xl border-r-4 border-tertiary p-4 [animation-delay:1s] shadow-2xl" : "glass absolute bottom-12 right-6 w-72 animate-float rounded-2xl border-l-4 border-tertiary p-4 [animation-delay:1s] shadow-2xl"}>
                  <div className="mb-2 flex items-center justify-between">
                    <span className="rounded-full bg-tertiary-fixed px-2 py-1 text-[10px] font-bold">DETECTED</span>
                    <span className="material-symbols-outlined text-tertiary">warning</span>
                  </div>
                  <p className="font-bold">Early Blight (Fungal)</p>
                  <p className="text-xs text-on-surface-variant">Apply organic neem oil and isolate from airflow path.</p>
                </div>
              </div>
            </div>
          </div>
        </section>

        <section className="bg-surface-container-low px-6 py-20 lg:px-12 dark:bg-slate-900">
          <div className="mx-auto max-w-7xl">
            <h2 className="mb-10 text-center text-4xl font-black tracking-tight">{t.landing.sectionTitle}</h2>
            <div className="grid auto-rows-[220px] grid-cols-1 gap-6 md:grid-cols-12">
              <div className="rounded-3xl bg-white p-8 shadow-soft md:col-span-8 dark:bg-slate-950">
                <p className="mb-2 text-3xl font-black">99.4% Recognition Accuracy</p>
                <p className="max-w-md text-on-surface-variant">Trained on over 2 million plant specimens across greenhouse and open-field conditions.</p>
              </div>
              <div className="relative overflow-hidden rounded-3xl bg-primary p-8 text-white md:col-span-4 md:row-span-2">
                <img src={imageUrls.leaf} alt="leaf" className="absolute inset-0 h-full w-full object-cover opacity-20" />
                <div className="relative">
                  <span className="material-symbols-outlined mb-3 text-4xl">clinical_notes</span>
                  <p className="text-3xl font-black">Treatment Plans</p>
                  <p className="mt-3 text-sm text-white/90">Science-backed recommendations customized for your environment.</p>
                </div>
              </div>
              <div className="rounded-3xl bg-surface-container p-8 text-center md:col-span-4 dark:bg-slate-800">
                <div className="mx-auto mb-3 flex h-14 w-14 items-center justify-center rounded-full bg-primary-fixed">
                  <span className="material-symbols-outlined text-on-primary-fixed">speed</span>
                </div>
                <p className="text-xl font-bold">Instant Results</p>
              </div>
              <div className="rounded-3xl border-l-4 border-tertiary bg-tertiary-fixed/20 p-8 md:col-span-4">
                <p className="font-bold text-tertiary">Pathogen Alerts</p>
                <p className="mt-2 text-sm text-on-surface-variant">Identify disease signatures early before crop-wide spread.</p>
              </div>
            </div>
          </div>
        </section>

        <section className="relative overflow-hidden bg-emerald-950 px-6 py-24 text-white lg:px-12">
          <div className="absolute -right-20 -top-20 h-64 w-64 rounded-full bg-emerald-700/40 blur-3xl" />
          <div className="mx-auto max-w-4xl text-center">
            <h3 className="text-4xl font-black lg:text-6xl">{t.landing.ctaBottom}</h3>
            <div className="mt-8 flex flex-col justify-center gap-4 sm:flex-row">
              <Link to="/workspace" className="rounded-2xl bg-white px-10 py-4 font-black text-emerald-950 transition hover:scale-105">
                {t.landing.ctaStart}
              </Link>
              <button className="rounded-2xl border border-emerald-500/50 px-10 py-4 font-bold transition hover:bg-emerald-900/50">
                {t.landing.ctaEnterprise}
              </button>
            </div>
          </div>
        </section>
      </div>
    </PageTransition>
  );
}