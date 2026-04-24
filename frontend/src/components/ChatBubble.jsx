import { cn } from "../utils/cn";
import { useI18n } from "../hooks/useI18n";
import { detectLanguage } from "../utils/api";

export default function ChatBubble({ message }) {
  const { t } = useI18n();
  const isUser = message.role === "user";
  const detectedLang = detectLanguage(message.text);
  const isRtl = detectedLang === "ar";

  return (
    <div className={cn("flex gap-4", isUser ? "justify-end" : "justify-start")}>
      {!isUser && (
        <div className="flex h-10 w-10 shrink-0 items-center justify-center rounded-full bg-primary-container text-on-primary-container">
          <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
            smart_toy
          </span>
        </div>
      )}
      <div className={cn("max-w-2xl", isUser ? "items-end" : "items-start")}>
        <div
          className={cn(
            "rounded-3xl p-5 shadow-sm",
            isUser ? "rounded-br-md bg-primary text-white" : "rounded-bl-md bg-white dark:bg-slate-900"
          )}
        >
          <p className="leading-7 whitespace-pre-wrap" dir={isRtl ? "rtl" : "ltr"}>
            {message.text}
          </p>
          {message.warning && (
            <div className="mt-4 rounded-xl border border-tertiary/20 bg-tertiary-fixed p-4 text-on-tertiary-fixed-variant">
              <div className="mb-1 flex items-center gap-2 text-sm font-bold">
                <span className="material-symbols-outlined text-base">warning</span>
                {t.assistant.warningTitle}
              </div>
              <p className="text-sm">{message.warning}</p>
            </div>
          )}
        </div>
        <p className="mt-2 text-xs text-outline">{message.time}</p>
      </div>
    </div>
  );
}