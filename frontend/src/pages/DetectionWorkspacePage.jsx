import { useState } from "react";
import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import Card from "../components/Card";
import UploadBox from "../components/UploadBox";
import ProgressBar from "../components/ProgressBar";
import { imageUrls } from "../data/mockData";
import { useI18n } from "../hooks/useI18n";

export default function DetectionWorkspacePage() {
  const { t } = useI18n();
  const [preview, setPreview] = useState("");

  const handleFile = (file) => {
    setPreview(URL.createObjectURL(file));
  };

  return (
    <PageTransition>
      <Layout title={t.detect.title} subtitle={t.detect.subtitle} sidebarOptions={{ showBrand: false, showUpgrade: false }}>
        <div className="mb-6 flex items-center justify-end gap-3">
          <button className="rounded-xl bg-surface-container px-5 py-3 text-sm font-semibold transition hover:bg-surface-container-high dark:bg-slate-800">
            {t.detect.guide}
          </button>
          <button className="rounded-xl bg-primary px-5 py-3 text-sm font-bold text-white shadow-lg transition hover:scale-95">
            {t.detect.newScan}
          </button>
        </div>

        <div className="grid grid-cols-1 gap-6 xl:grid-cols-12">
          <div className="space-y-6 xl:col-span-3">
            <Card>
              <h3 className="mb-3 text-lg font-black uppercase tracking-wider">Batch Status</h3>
              <div className="rounded-2xl bg-surface-container p-3 dark:bg-slate-800">
                <p className="font-semibold">No file uploaded</p>
                <p className="text-sm text-on-surface-variant">Waiting for upload...</p>
              </div>
            </Card>
          </div>

          <div className="xl:col-span-5">
            <UploadBox onFile={handleFile} preview={preview} />
            <Card className="mt-6 text-center">
              <div className="mx-auto mb-3 w-fit rounded-full bg-primary-fixed px-3 py-1 text-xs font-bold text-on-primary-fixed">NEURAL_CORE_v2</div>
              <h3 className="mb-4 text-3xl font-black">AI ready for analysis</h3>
              <ProgressBar value={0} />
              <p className="mt-4 text-sm text-on-surface-variant">
                Identifying pathogen markers: <span className="font-semibold italic text-primary">0%</span>
              </p>
              <button className="mt-4 text-sm font-bold uppercase tracking-wider text-tertiary/60">{t.detect.cancel}</button>
            </Card>
          </div>

          <div className="space-y-6 xl:col-span-4">
            <Card>
              <h3 className="mb-4 text-lg font-black uppercase tracking-wider">{t.detect.metadata}</h3>
              <div className="space-y-3 text-sm">
                <div className="flex items-center justify-between"><span>Filename</span><span className="font-semibold">IMG_4829.HEIC</span></div>
                <div className="flex items-center justify-between"><span>Resolution</span><span className="font-semibold">12 MP</span></div>
                <div className="flex items-center justify-between"><span>Light Index</span><span className="font-semibold text-primary">Optimal</span></div>
              </div>
            </Card>

            <Card>
              <img src={imageUrls.greenhouse} alt="greenhouse" className="h-40 w-full rounded-2xl object-cover" />
              <p className="mt-3 text-sm text-on-surface-variant">Neural Engine: Active</p>
            </Card>
          </div>
        </div>
      </Layout>
    </PageTransition>
  );
}