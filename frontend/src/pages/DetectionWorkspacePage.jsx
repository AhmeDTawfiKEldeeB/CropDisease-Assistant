import { useState, useCallback } from "react";
import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import Card from "../components/Card";
import UploadBox from "../components/UploadBox";
import ProgressBar from "../components/ProgressBar";
import { useI18n } from "../hooks/useI18n";
import { detectImage } from "../utils/api";

function formatDiseaseName(name) {
  return name.replace(/_/g, " ").replace(/___/g, " - ");
}

export default function DetectionWorkspacePage() {
  const { t } = useI18n();
  const [preview, setPreview] = useState("");
  const [fileName, setFileName] = useState("");
  const [file, setFile] = useState(null);
  const [scanning, setScanning] = useState(false);
  const [progress, setProgress] = useState(0);
  const [statusText, setStatusText] = useState("Waiting for upload");
  const [error, setError] = useState("");
  const [result, setResult] = useState(null);

  const handleFile = useCallback((f) => {
    setPreview(URL.createObjectURL(f));
    setFileName(f.name);
    setFile(f);
    setError("");
    setProgress(0);
    setStatusText("Waiting for upload");
    setResult(null);
  }, []);

  const handleScan = useCallback(async () => {
    if (!file) return;
    setScanning(true);
    setError("");
    setProgress(30);
    setStatusText("Analyzing leaf image...");
    setResult(null);

    try {
      const res = await detectImage(file);
      setResult(res);
      setProgress(100);
      setStatusText(formatDiseaseName(res.top_class));
    } catch (err) {
      setError(err.message || "Prediction failed");
      setProgress(0);
      setStatusText("Error");
    } finally {
      setScanning(false);
    }
  }, [file]);

  const handleCancel = useCallback(() => {
    setScanning(false);
    setProgress(0);
    setStatusText("Waiting for upload");
    setResult(null);
  }, []);

  const checklist = [
    "Use a sharp, well-lit leaf photo.",
    "Keep the target leaf centered and in focus.",
    "Avoid heavy shadows and blurry motion.",
  ];

  return (
    <PageTransition>
      <Layout title={t.detect.title} subtitle={t.detect.subtitle} sidebarOptions={{ showBrand: false }}>
        <div className="relative overflow-hidden rounded-[2rem] border border-surface-variant/30 bg-gradient-to-br from-white via-[#f7faf6] to-[#eef8f0] p-4 shadow-[0_24px_70px_rgba(16,56,38,0.08)] md:p-6">
          <div className="absolute -left-24 top-16 h-64 w-64 rounded-full bg-[#235f34]/18 blur-3xl" />
          <div className="absolute -right-24 bottom-8 h-72 w-72 rounded-full bg-[#235f34]/12 blur-3xl" />

          <div className="relative grid grid-cols-1 gap-6 xl:grid-cols-[1.18fr_0.82fr] xl:gap-8">
            <div className="space-y-6">
              <UploadBox onFile={handleFile} preview={preview} fileName={fileName} />

              <Card className="overflow-hidden border-[#235f34]/12 bg-white/90 p-0 shadow-[0_24px_60px_rgba(16,56,38,0.08)]">
                <div className="border-b border-[#235f34]/12 bg-gradient-to-r from-[#eaf3e7] to-white px-6 py-4">
                  <div className="flex items-center justify-between gap-3">
                    <div>
                      <div className="mb-1 w-fit rounded-full bg-[#235f34] px-3 py-1 text-xs font-bold text-white">NEURAL_CORE_v2</div>
                      <h3 className="text-2xl font-black tracking-tight">AI ready for analysis</h3>
                    </div>
                    <span className="material-symbols-outlined text-[#235f34]">science</span>
                  </div>
                </div>

                <div className="space-y-5 px-6 py-6">
                  <ProgressBar value={progress} />
                  <div className="flex items-center justify-between text-sm text-on-surface-variant">
                    <span>Identifying pathogen markers</span>
                    <span className="font-semibold italic text-primary">{progress}%</span>
                  </div>
                  <div className="flex items-center justify-between gap-3 rounded-2xl bg-surface-container-low px-4 py-3">
                    <span className="text-sm font-medium text-on-surface">Status</span>
                    <span className={`text-sm font-semibold ${error ? "text-red-600" : result ? "text-[#235f34]" : "text-[#235f34]"}`}>
                      {error || statusText}
                    </span>
                  </div>
                  {result && (
                    <div className="rounded-2xl bg-[#eaf3e7] px-4 py-3 text-center">
                      <p className="text-xs font-bold uppercase tracking-wider text-[#235f34]">Detected Disease</p>
                      <p className="mt-1 text-lg font-bold text-[#235f34]">{statusText}</p>
                      <p className="mt-1 text-sm text-on-surface-variant">Confidence: {Math.round(result.top_confidence)}%</p>
                    </div>
                  )}
                  {preview && !scanning && !result && !error && (
                    <button
                      onClick={handleScan}
                      className="w-full rounded-xl bg-[#235f34] py-3 text-sm font-bold uppercase tracking-wider text-white transition hover:bg-[#1a4a28]"
                    >
                      Start Diagnosis
                    </button>
                  )}
                  {(scanning || result) && (
                    <button
                      onClick={handleCancel}
                      className="text-sm font-bold uppercase tracking-wider text-tertiary/70 transition hover:text-tertiary"
                    >
                      {t.detect.cancel}
                    </button>
                  )}
                </div>
              </Card>
            </div>

            <div className="space-y-6 xl:pt-1">
              <Card className="overflow-hidden border-[#235f34]/12 bg-white/90 p-0 shadow-[0_24px_60px_rgba(16,56,38,0.08)]">
                <div className="border-b border-[#235f34]/12 px-6 py-5">
                  <p className="text-xs font-bold uppercase tracking-[0.22em] text-[#235f34]">Guided capture</p>
                  <h3 className="mt-2 text-2xl font-black tracking-tight">Get the cleanest scan</h3>
                  <p className="mt-2 text-sm leading-6 text-on-surface-variant">
                    Keep the image sharp and centered so the model can read the leaf structure clearly.
                  </p>
                </div>

                <div className="space-y-4 px-6 py-5">
                  {checklist.map((item) => (
                    <div key={item} className="flex items-start gap-3 rounded-2xl bg-[#eaf3e7] px-4 py-3">
                      <span className="material-symbols-outlined mt-0.5 text-[20px] text-[#235f34]">check_circle</span>
                      <p className="text-sm leading-6 text-on-surface-variant">{item}</p>
                    </div>
                  ))}
                </div>
              </Card>

              <Card className="border-[#235f34]/12 bg-white/80 p-5 shadow-[0_18px_50px_rgba(16,56,38,0.06)] backdrop-blur">
                <div className="flex items-start gap-4">
                  <div className="flex h-11 w-11 shrink-0 items-center justify-center rounded-2xl bg-[#235f34] text-white">
                    <span className="material-symbols-outlined text-[24px]">schedule</span>
                  </div>
                  <div>
                    <p className="text-sm font-semibold text-on-surface">Workflow direction</p>
                    <p className="mt-1 text-sm leading-6 text-on-surface-variant">
                      Upload on the left, review the scan status below, and keep the capture guide aligned on the right.
                    </p>
                  </div>
                </div>
              </Card>
            </div>
          </div>
        </div>
      </Layout>
    </PageTransition>
  );
}
