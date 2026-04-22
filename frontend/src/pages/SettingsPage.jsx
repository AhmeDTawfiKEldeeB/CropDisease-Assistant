import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import Card from "../components/Card";
import LanguageToggle from "../components/LanguageToggle";
import { useI18n } from "../hooks/useI18n";

export default function SettingsPage() {
  const { t } = useI18n();

  return (
    <PageTransition>
      <Layout title={t.settings.title} subtitle={t.settings.subtitle}>
        <div className="grid grid-cols-1 gap-6 xl:grid-cols-2">
          <Card>
            <h3 className="mb-4 text-2xl font-black">{t.settings.language}</h3>
            <p className="mb-6 text-on-surface-variant">Switch application language instantly with RTL/LTR direction support.</p>
            <LanguageToggle />
          </Card>

          <Card>
            <h3 className="mb-4 text-2xl font-black">{t.settings.notifications}</h3>
            <div className="space-y-3 text-sm">
              <label className="flex items-center justify-between rounded-2xl bg-surface-container p-4 dark:bg-slate-800">
                <span>Disease Alert Push Notifications</span>
                <input type="checkbox" defaultChecked className="h-4 w-4 accent-primary" />
              </label>
              <label className="flex items-center justify-between rounded-2xl bg-surface-container p-4 dark:bg-slate-800">
                <span>Weekly Insight Digest</span>
                <input type="checkbox" defaultChecked className="h-4 w-4 accent-primary" />
              </label>
            </div>
          </Card>

          <Card>
            <h3 className="mb-4 text-2xl font-black">{t.settings.model}</h3>
            <p className="mb-3 text-sm text-on-surface-variant">Detection strictness</p>
            <input type="range" defaultValue={76} className="w-full accent-primary" />
            <p className="mt-6 mb-3 text-sm text-on-surface-variant">Auto-generate treatment plans</p>
            <input type="checkbox" defaultChecked className="h-4 w-4 accent-primary" />
          </Card>
        </div>

        <button className="mt-8 rounded-xl bg-primary px-8 py-3 text-lg font-bold text-white shadow-lg transition hover:scale-[1.02]">
          {t.settings.save}
        </button>
      </Layout>
    </PageTransition>
  );
}