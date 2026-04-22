import { Link } from "react-router-dom";
import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import Card from "../components/Card";
import ProgressBar from "../components/ProgressBar";
import { imageUrls } from "../data/mockData";
import { useI18n } from "../hooks/useI18n";

export default function DiagnosisPage() {
  const { t, isRTL } = useI18n();

  return (
    <PageTransition>
      <Layout title={t.diagnosis.plant} subtitle={t.diagnosis.breadcrumb}>
        <div className="relative mb-6 overflow-hidden rounded-3xl">
          <img src={imageUrls.leaf} alt="diagnosis" className="h-[420px] w-full object-cover" />
          <div className="absolute inset-x-0 bottom-0 flex justify-end gap-3 p-5">
            <button className="rounded-full bg-black/30 p-3 text-white backdrop-blur transition hover:scale-105">
              <span className="material-symbols-outlined">zoom_in</span>
            </button>
            <button className="rounded-full bg-black/30 p-3 text-white backdrop-blur transition hover:scale-105">
              <span className="material-symbols-outlined">share</span>
            </button>
          </div>
        </div>

        <div className={isRTL ? "mb-6 rounded-3xl border-r-8 border-tertiary bg-tertiary-fixed/30 p-6" : "mb-6 rounded-3xl border-l-8 border-tertiary bg-tertiary-fixed/30 p-6"}>
          <h2 className="text-3xl font-black text-on-tertiary-fixed-variant">{t.diagnosis.title}</h2>
          <p className="mt-1 italic text-on-tertiary-fixed-variant/80">{t.diagnosis.scientific}</p>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-3">
          <Card>
            <div className="mb-3 flex items-center justify-between">
              <p className="text-sm font-bold uppercase tracking-wider text-on-surface-variant">{t.diagnosis.confidence}</p>
              <p className="text-5xl font-black text-primary">98%</p>
            </div>
            <ProgressBar value={98} />
            <p className="mt-3 text-sm italic text-on-surface-variant">Model v4.2 Botanical AI</p>
          </Card>
          <Card className="xl:col-span-2">
            <div className="flex items-start gap-4">
              <div className="rounded-xl bg-primary/10 p-3 text-primary">
                <span className="material-symbols-outlined">description</span>
              </div>
              <div>
                <h3 className="text-2xl font-black">{t.diagnosis.needPlan}</h3>
                <p className="mt-1 text-on-surface-variant">{t.diagnosis.desc}</p>
              </div>
            </div>
            <Link
              to="/assistant"
              className="mt-5 flex w-full items-center justify-center gap-2 rounded-xl bg-primary px-6 py-3 text-center text-lg font-bold text-white shadow-lg transition hover:scale-[1.01]"
            >
              {t.diagnosis.action}
              <span className="material-symbols-outlined">{isRTL ? "chevron_left" : "chevron_right"}</span>
            </Link>
          </Card>
        </div>
      </Layout>
    </PageTransition>
  );
}