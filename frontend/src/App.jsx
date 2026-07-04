import { useEffect, useMemo } from "react";
import { AnimatePresence } from "framer-motion";
import { Navigate, Route, Routes, useLocation } from "react-router-dom";
import LandingPage from "./pages/LandingPage";
import DetectionWorkspacePage from "./pages/DetectionWorkspacePage";
import AssistantPage from "./pages/AssistantPage";
import HistoryPage from "./pages/HistoryPage";
import SettingsPage from "./pages/SettingsPage";
import { I18nProvider } from "./hooks/useI18n";

export default function App() {
  const lang = "en";
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
      t: {
        appName: "Digital Greenhouse",
        top: { theme: "Theme" },
        nav: {
          home: "Home",
          detect: "Detect Disease",
          assistant: "Assistant",
          upgrade: "Upgrade",
          help: "Help",
          signOut: "Sign Out",
        },
        assistant: { warningTitle: "Safety note" },
        detect: {
          title: "Detection Workspace",
          subtitle: "Upload a leaf image and review the scan results.",
          cancel: "Cancel Diagnosis",
        },
        diagnosis: {
          plant: "Plant Diagnosis",
          breadcrumb: "Diagnosis Overview",
          title: "Disease detected",
          scientific: "Based on the uploaded image and symptom pattern.",
          confidence: "Confidence",
          needPlan: "Treatment plan",
          desc: "Review the recommended treatment steps and follow-up guidance.",
          action: "Open Assistant",
        },
        history: {
          title: "History",
          subtitle: "Review past disease scans and outcomes.",
          recent: "Recent scans",
          details: "View Details",
        },
        settings: {
          title: "Settings",
          subtitle: "Adjust application preferences and model behavior.",
          language: "Language",
          notifications: "Notifications",
          model: "Model",
          save: "Save Changes",
        },
      },
      toggleLang: () => undefined,
      toggleTheme: () => undefined,
    }),
    [lang, isRTL]
  );

  return (
    <I18nProvider value={i18nValue}>
      <AnimatePresence mode="wait">
        <Routes location={location} key={location.pathname}>
          <Route path="/" element={<LandingPage />} />
          <Route path="/workspace" element={<DetectionWorkspacePage />} />
          <Route path="/assistant" element={<AssistantPage />} />
          <Route path="/history" element={<HistoryPage />} />
          <Route path="/settings" element={<SettingsPage />} />
          <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
      </AnimatePresence>
    </I18nProvider>
  );
}