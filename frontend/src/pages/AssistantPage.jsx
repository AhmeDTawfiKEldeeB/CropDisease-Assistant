import { useState, useRef, useEffect } from "react";
import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import ChatBubble from "../components/ChatBubble";
import Card from "../components/Card";
import TypingIndicator from "../components/TypingIndicator";
import { imageUrls } from "../data/mockData";
import { useI18n } from "../hooks/useI18n";
import { sendChatMessage } from "../utils/api";

let nextId = 1;

export default function AssistantPage() {
  const { t, lang } = useI18n();
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  const handleSend = async () => {
    const question = draft.trim();
    if (!question || loading) return;

    const userMsg = {
      id: nextId++,
      role: "user",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      text: question,
    };

    setMessages((prev) => [...prev, userMsg]);
    setDraft("");
    setLoading(true);

    try {
      const history = messages
        .filter((m) => (m.role === "user" || m.role === "ai") && m.text)
        .map((m) => ({
          role: m.role === "ai" ? "assistant" : "user",
          content: m.text,
        }));

      const data = await sendChatMessage(question, 5, history);

      const aiMsg = {
        id: nextId++,
        role: "ai",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        text: data.answer || "I couldn't generate a response.",
        warning: data.retrieval_error || undefined,
      };

      setMessages((prev) => [...prev, aiMsg]);
    } catch (err) {
      const errMsg = {
        id: nextId++,
        role: "ai",
        time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
        text: err instanceof Error ? err.message : "An error occurred",
      };
      setMessages((prev) => [...prev, errMsg]);
    } finally {
      setLoading(false);
    }
  };

  const handleKeyDown = (e) => {
    if (e.key === "Enter" && !e.shiftKey) {
      e.preventDefault();
      handleSend();
    }
  };

  return (
    <PageTransition>
      <Layout title={t.assistant.title} subtitle={lang === "ar" ? "تم الكشف في 24 فبراير • جلسة الذكاء الاصطناعي نشطة" : "Detected on Feb 24 • AI Session Active"}>
        <div className="grid grid-cols-1 gap-6 2xl:grid-cols-12">
          <div className="space-y-6 2xl:col-span-3">
            <Card>
              <h3 className="mb-4 text-xl font-black">Specimen Details</h3>
              <div className="mb-3 flex items-center gap-2 text-sm">
                <span className="rounded-full bg-tertiary-fixed px-2 py-1 text-[10px] font-bold uppercase text-on-tertiary-fixed-variant">Critical</span>
                <span className="text-on-surface-variant">Alert Level</span>
              </div>
              <div className="h-2 overflow-hidden rounded-full bg-surface-container-high dark:bg-slate-800">
                <div className="h-full w-[85%] rounded-full bg-tertiary" />
              </div>
              <p className="mt-3 text-sm text-on-surface-variant">Confidence level: 94.2%</p>
            </Card>
            <Card>
              <img src={imageUrls.greenhouse} alt="zone" className="h-44 w-full rounded-2xl object-cover" />
              <p className="mt-3 text-lg font-bold">Climate Overview</p>
            </Card>
          </div>

          <div className="2xl:col-span-9">
            <div ref={scrollRef} className="mb-6 max-h-[62vh] space-y-6 overflow-y-auto rounded-3xl bg-surface-container-low p-6 hide-scrollbar dark:bg-slate-900">
              <div className="flex justify-center">
                <span className="rounded-full bg-surface-container px-3 py-1 text-xs font-bold uppercase tracking-wider text-outline dark:bg-slate-800">Today</span>
              </div>
              {messages.map((message) => (
                <ChatBubble key={message.id} message={message} />
              ))}
              {loading && <TypingIndicator />}
              {messages.length === 0 && !loading ? (
                <div className="flex min-h-[340px] items-center justify-center">
                  <div className="text-center">
                    <div className="mx-auto mb-4 flex h-16 w-16 items-center justify-center rounded-full bg-primary/10 text-primary">
                      <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                        smart_toy
                      </span>
                    </div>
                    <p className="text-xl font-bold text-on-surface">Start a new conversation</p>
                    <p className="mt-2 text-sm text-on-surface-variant">Upload an image or ask your first question to begin diagnosis assistance.</p>
                  </div>
                </div>
              ) : null}
            </div>

            <div className="glass rounded-2xl border border-outline-variant/30 p-2 shadow-soft dark:border-slate-700">
              <div className="flex items-end gap-2">
                <button className="p-3 text-outline transition hover:text-primary">
                  <span className="material-symbols-outlined">attach_file</span>
                </button>
                <textarea
                  rows={1}
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={t.assistant.placeholder}
                  className="max-h-40 min-h-[44px] flex-1 resize-none bg-transparent px-2 py-3 outline-none"
                />
                <button className="p-3 text-outline transition hover:text-primary">
                  <span className="material-symbols-outlined">mic</span>
                </button>
                <button
                  onClick={handleSend}
                  disabled={loading || !draft.trim()}
                  className="rounded-xl bg-primary p-3 text-white shadow-lg transition hover:scale-105 disabled:opacity-50 disabled:hover:scale-100"
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                    send
                  </span>
                </button>
              </div>
            </div>
          </div>
        </div>
      </Layout>
    </PageTransition>
  );
}