import { useEffect, useMemo } from "react";
import { AnimatePresence } from "framer-motion";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import DetectionWorkspacePage from "./pages/DetectionWorkspacePage";
import DiagnosisPage from "./pages/DiagnosisPage";
import AssistantPage from "./pages/AssistantPage";
import HistoryPage from "./pages/HistoryPage";
import SettingsPage from "./pages/SettingsPage";
import { useLocalStorage } from "./hooks/useLocalStorage";
import { I18nProvider } from "./hooks/useI18n";
import { translations } from "./data/translations";

export default function App() {
  const [lang, setLang] = useLocalStorage("florascan_lang", "en");
  const location = useLocation();
  const isRTL = lang === "ar";

  useEffect(() => {
    document.documentElement.lang = lang;
    document.documentElement.dir = isRTL ? "rtl" : "ltr";
    document.documentElement.classList.remove("dark");
  }, [lang, isRTL]);

  const i18nValue = useMemo(
    () => ({
      lang,
      theme: "light",
      isRTL,
      t: translations[lang],
      toggleLang: () => setLang((prev) => (prev === "en" ? "ar" : "en")),
      toggleTheme: () => undefined,
    }),
    [lang, isRTL, setLang]
  );

  return (
    <I18nProvider value={i18nValue}>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/workspace" element={<DetectionWorkspacePage />} />
          <Route path="/diagnosis" element={<DiagnosisPage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </I18nProvider>
  );
}