import { useI18n } from "../hooks/useI18n";

export default function LanguageToggle() {
  const { toggleLang, t } = useI18n();
  return (
    <button
      onClick={toggleLang}
      className="rounded-full bg-primary-fixed px-4 py-2 text-xs font-bold text-on-primary-fixed transition hover:scale-95"
    >
      {t.top.language}
    </button>
  );
}