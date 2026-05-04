import { useMemo, useRef, useEffect, useState } from "react";
import { AnimatePresence, motion } from "framer-motion";
import Layout from "../components/Layout";
import PageTransition from "../components/PageTransition";
import ChatBubble from "../components/ChatBubble";
import TypingIndicator from "../components/TypingIndicator";
import { sendChatMessage } from "../utils/api";

let nextId = 1;

const plants = [
  {
    id: "Apple",
    name: "Apple",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBS998xd4yi7pOEP_ZzjYvc1BeOYhFNyWlG2FocG-IZKZZXlwSDSBexsYNw4nV6IK-mzQZORadIyjgu6K94kF3BcFLhty2tpujqjyeFAPd8jkMzmV0IcxQ0mTr4Uupl3dTDSEjOXOgxARCFRGo8xjwS45RRsW3DKY4WGvKI6d_d5VyOb2OIkQOosF8JnxIssVsjkL_RCn-Ss02gClVjT6KcNXSsQBMFdHkGiXcuU45Y9Yihz3A01gZHW_VKNU0UlmF61Cdv0kJ4mN4",
  },
  {
    id: "Cherry",
    name: "Cherry",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBEucCUQFDWdAxffnPwOnUdE9LEmq2rrp0hsOA5GFb3L-ngTjHLiddSXa96oVS9ADpi4TCuwU7PFP6bjwJVdDmuAHavGk6ghXhCQT7n5M17bAjgb7zY-Ken50yIpl_SvqGxEQb0LKYp7TNrTjQ70TQX3KyHiBzeHMZ8FwuWtxFwBK9FsjkiOsPIJfSop2sY6NcxUQ4ausR1elZteYWWpIjzDwjDjxgitC05j3KkYXZYrhC3NPE03R2U2fQaQJ_tHLAKPfB6qLTgHHg",
  },
  {
    id: "Corn (Maize)",
    name: "Corn",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuDWAyL7fnamuxcXA2NGXXwm4gtiO66ltihATn-Gmfymhr-GhIeBaH5yIw1f2IIJ7TjNQHFUdQPUUIDsvLGAh1_sPbYF9opJz3hTRKkeR9iLNvtPzIq5EKQgEqNyOxEcN18qkYoK2xg-VO4VHkSGtdm4Mu1hprV-MrflvqigD6xylfc5BIFzIzPVssa_-rbb3IaNHlUc2E6l-HqzNdKDJsExvOTDUWBWcwUysH9U0EprRY8Lnl_ay1ifxjVMyiqfcPupFR2JV0Dk5k4",
  },
  {
    id: "Grape",
    name: "Grape",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuC-g4rq-DgX55hEhX-Y1w6DVUakMPmIpH6cpsMadCN4HGoyV02wQ-v4jecgCuCj3GCX8xXqD7xqZHz9ufgme0uCvPAFv_w8mV1IDz1pPDSW4nE97pgEkyaJ8eKzc_gddGz6DnF_MX5gSoBeN0tS_rZaLnMYljHMoZhtaXdUHKyEMPdrjFclYbbLa-llB87at-6vx6rRNYoVKQs_7FefkWMUA9u3kAsAlPGm5ZQ0VLk4lwjK4Ia4TIlKCXpVIdje_QXNgq4N5uO8Los",
  },
  {
    id: "Orange",
    name: "Orange",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBnaZR-i--I1EnewjDdcWVO8pAMGa9e2P3kZi0INrxi_lJ0TDfx0pwd0mJYEf6vJ11pSdicprkrMTdAoT6d0r_uvUtao2PQ9iuERZ1WGHZ24Nqc9MmoPJNMgiPlsimB_rebYFjboRRlwyEaAP9xZx2IfAEGH7s2DXbRcvkZ3bIah-e9P5X_IvGKalcj1sMhwmqXO7sotdhet1fX7OEGcaiXGE4vzgkhJDxD_guCiTekxtdbSDna04rz4LGS_JGPpBzlA7-SgX9K824",
  },
  {
    id: "Peach",
    name: "Peach",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuCUZkVJbrECU4LZ4XsG5OY9v4Zaomh5B7UHyb9UrbyB7GQWI5AzytlWo4tXM3D33333iljxE3syxUjGZpkf0SrjIGvGUmLkwgGMdFooMN3WAEcEiwKfLO1KJxfEtCwKqRPaAWRnfCTPbcTOshqK_Un12ULqMnkf7KYjVi79JNiqkfmOJ_J8yTXfIEsZWLfQyx-gxGMpoNIQMenQU5Af5Wjkwqy-KKAwRnGJFe3qO-vyzPZ8TA1WBLPh1PWeMdTpU9BQRACHyQKlMJU",
  },
  {
    id: "Pepper (Bell)",
    name: "Pepper",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuAjNpz6qjT3cZG247ouC-cnngyyvCGG3NzC1undqIHFgjRRw7qcTRBVI_ldo0I1rWxxAQw3YNNee-pke5oZG8jEszWxTwOXZBA2e7grTt6wnaqca12dR3rb5Hk0b61HSaf4pUjQMnbzsf9EPuYLHbp0EilcRT8J2BbXjcBUtHf2iXoauTa-t00n_s61_Q3FXvgP2TziWEeZ9c-Z-ZjjlZfwXX_NbyjsFcaweRAMDAPXkhjpGWhDSYo1iIvdaN_Su1rjWilHScr4kWg",
  },
  {
    id: "Potato",
    name: "Potato",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuDqOWcUHD5Lf32H8ro97yaakoN9Xnjh6tvHR0R-9aqSfvHB1iPTLZaqbEu0ObJC6WR3De5XocXqTZHxchVBAd9PTksiW1bjaYxcHwGl5fsWPzikmu80zGCJeLHgYPvDCYJreVBV04OEk4HMR-GOfcunCtiy3Jm0krfuhySTETJ2XmQ4ZicseJ303hXxrxW1ffFkwmTfZvMX7XZrHjLw7MVyBzbexR2K2HMaJ4Pd4C3_2AMfervAKWTdroaUDULWz3bRgZ17z1isKJ0",
  },
  {
    id: "Strawberry",
    name: "Strawberry",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuBXshpNPyJ2470kn2ofgqHKEx7AaP4wSTZZWaL-SBxvXJoYfzrbEuuKF1IlYKp4cfp3NNZVBTy52D3_9kO30B3pOHFh3B02dY-5_oideOVUOEyQUoNpOMKQN8SVfyhSH1a3N9jrSQMpsFNzPHAaY-K4wNTt8mh5wngyLULYOntWokxAGBY5pG-Ea3HlYlndsrzcz1ScbzIZOiIIuVn4la335y61nz3IBazGMR1TTVcwGz5P-s3lNzjNIm4axh-vI4DiYt9JvZ7ic6E",
  },
  {
    id: "Tomato",
    name: "Tomato",
    image:
      "https://lh3.googleusercontent.com/aida-public/AB6AXuC-MIJhjhk_xv3EBSjXBG-nxAwt3G9vLaThbqpW3ckKDq1tcs_xskaL-cA-MeyIkSIvck9yymg_0HXVQJ0DfZM4Cod8rO0LJmOoEzTNwdXlf182SKy8HHtodOZySGGRP6dr1r-FlclPT1Tir4U1becXmtmi57d-4xXxL43oEgdQJn7iEIAiLCAGwQF8b1W-7T4L_7ubhzHeo2gQ1WsXSq-718gDvknWa0aePri4XE6Rm43YfeKU3FcR8F7OBIJEMSUBmmsuewnP4c0",
  },
];

const diseasesByPlant = {
  Apple: ["Apple Scab", "Black Rot", "Cedar Apple Rust"],
  Blueberry: [],
  Cherry: ["Powdery Mildew"],
  "Corn (Maize)": [
    "Cercospora Leaf Spot (Gray Leaf Spot)",
    "Common Rust",
    "Northern Leaf Blight",
  ],
  Grape: [
    "Black Rot",
    "Esca (Black Measles)",
    "Leaf Blight (Isariopsis Leaf Spot)",
  ],
  Orange: ["Huanglongbing (Citrus Greening)"],
  Peach: ["Bacterial Spot"],
  "Pepper (Bell)": ["Bacterial Spot"],
  Potato: ["Early Blight", "Late Blight"],
  Strawberry: ["Leaf Scorch"],
  Tomato: [
    "Bacterial Spot",
    "Early Blight",
    "Late Blight",
    "Leaf Mold",
    "Septoria Leaf Spot",
    "Spider Mites (Two-spotted)",
    "Target Spot",
    "Yellow Leaf Curl Virus",
    "Mosaic Virus",
  ],
};

export default function AssistantPage() {
  const [selectedPlant, setSelectedPlant] = useState(null);
  const [selectedDisease, setSelectedDisease] = useState(null);
  const [draft, setDraft] = useState("");
  const [messages, setMessages] = useState([]);
  const [loading, setLoading] = useState(false);
  const scrollRef = useRef(null);

  const step = selectedPlant ? (selectedDisease ? "chat" : "diseases") : "plants";

  const diseaseList = useMemo(() => {
    if (!selectedPlant) return [];
    return diseasesByPlant[selectedPlant] || [];
  }, [selectedPlant]);

  const selectedPlantData = useMemo(() => {
    if (!selectedPlant) return null;
    return plants.find((plant) => plant.id === selectedPlant) || null;
  }, [selectedPlant]);

  const selectedPlantImage = selectedPlantData?.image || "";
  const selectedPlantLabel = selectedPlantData?.name || selectedPlant;

  useEffect(() => {
    scrollRef.current?.scrollTo({ top: scrollRef.current.scrollHeight, behavior: "smooth" });
  }, [messages, loading]);

  useEffect(() => {
    if (!selectedDisease || !selectedPlant) return;
    const intro = {
      id: nextId++,
      role: "ai",
      time: new Date().toLocaleTimeString([], { hour: "2-digit", minute: "2-digit" }),
      text: `Ask me anything about ${selectedDisease} on ${selectedPlant}. I can explain spread, risk, and treatment options.`,
    };
    setMessages([intro]);
  }, [selectedDisease, selectedPlant]);

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
      const data = await sendChatMessage(question);

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

  const resetToPlants = () => {
    setSelectedPlant(null);
    setSelectedDisease(null);
    setMessages([]);
    setDraft("");
  };

  const resetToDiseases = () => {
    setSelectedDisease(null);
    setMessages([]);
    setDraft("");
  };

  return (
    <PageTransition>
      <Layout title="Smart Plant Assistant" subtitle="Select a plant, choose a disease, then chat with the assistant.">
        <AnimatePresence mode="wait">
          {step === "plants" ? (
            <motion.div
              key="plants"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="space-y-8"
            >
              <header>
                <h2 className="text-3xl font-black tracking-tight">Select Specimen</h2>
                <p className="mt-2 text-sm text-on-surface-variant">
                  Choose the plant species you wish to analyze. Our models are tuned for these varieties.
                </p>
              </header>
              <div className="grid grid-cols-2 gap-6 md:grid-cols-3 lg:grid-cols-4">
                {plants.map((plant) => (
                  <button
                    key={plant.id}
                    onClick={() => setSelectedPlant(plant.id)}
                    className="group relative aspect-square overflow-hidden rounded-lg shadow-sm transition-all duration-300 hover:-translate-y-1 hover:shadow-lg focus:outline-none focus:ring-4 focus:ring-primary-container/50"
                  >
                    <img src={plant.image} alt={plant.name} className="h-full w-full object-cover transition-transform duration-500 group-hover:scale-110" />
                    <div className="absolute inset-x-0 bottom-0 flex items-end justify-center bg-gradient-to-t from-black/80 via-black/40 to-transparent p-4 opacity-0 transition-opacity duration-300 group-hover:opacity-100">
                      <span className="text-sm font-bold text-white drop-shadow-md">{plant.name}</span>
                    </div>
                  </button>
                ))}
              </div>
            </motion.div>
          ) : null}

          {step === "diseases" ? (
            <motion.div
              key="diseases"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="space-y-8"
            >
              <div className="flex flex-wrap items-center gap-3 text-sm">
                <button
                  onClick={resetToPlants}
                  className="rounded-full border border-outline-variant/50 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-on-surface-variant transition hover:border-primary hover:text-primary"
                >
                  Change plant
                </button>
                <span className="text-on-surface-variant">Selected: {selectedPlantLabel}</span>
              </div>

              <div className="overflow-hidden rounded-2xl border border-outline-variant bg-surface-container shadow-sm">
                <div className="relative h-52 w-full">
                  <img src={selectedPlantImage} alt={selectedPlantLabel} className="h-full w-full object-cover" />
                  <div className="absolute inset-0 bg-gradient-to-t from-surface-container-highest to-transparent mix-blend-multiply" />
                  <div className="absolute bottom-6 left-6 rounded-2xl border border-white/20 bg-white/40 p-4 backdrop-blur-md">
                    <p className="text-xs font-bold uppercase tracking-widest text-on-surface-variant">Target Specimen</p>
                    <h2 className="text-3xl font-black text-on-surface">{selectedPlantLabel}</h2>
                  </div>
                </div>
                <div className="border-t border-outline-variant/30 bg-surface-container p-6">
                  <h3 className="text-lg font-bold">Select Disease for Analysis</h3>
                  <p className="mt-1 text-sm text-on-surface-variant">Choose the suspected condition to open a chat session.</p>
                </div>
              </div>

              <div className="grid grid-cols-1 gap-4 md:grid-cols-2 lg:grid-cols-3">
                {diseaseList.map((disease) => (
                  <button
                    key={disease}
                    onClick={() => setSelectedDisease(disease)}
                    className="group rounded-2xl border-l-[8px] border-tertiary bg-surface-container p-6 text-left shadow-sm transition hover:bg-surface-container-high"
                  >
                    <div className="mb-4 flex items-start justify-between">
                      <div className="rounded-full bg-tertiary-fixed p-3 text-on-tertiary-fixed">
                        <span className="material-symbols-outlined">biotech</span>
                      </div>
                      <span className="material-symbols-outlined text-outline-variant transition-colors group-hover:text-primary">
                        chevron_right
                      </span>
                    </div>
                    <h4 className="text-lg font-bold text-on-surface transition-colors group-hover:text-primary">{disease}</h4>
                    <p className="mt-2 text-sm text-on-surface-variant">Open the assistant for guidance on this condition.</p>
                  </button>
                ))}
              </div>
            </motion.div>
          ) : null}

          {step === "chat" ? (
            <motion.div
              key="chat"
              initial={{ opacity: 0, y: 16 }}
              animate={{ opacity: 1, y: 0 }}
              exit={{ opacity: 0, y: -12 }}
              transition={{ duration: 0.35, ease: "easeOut" }}
              className="flex h-[calc(100vh-220px)] flex-col"
            >
            <div className="mb-4 flex flex-wrap items-center gap-3 text-sm">
              <button
                onClick={resetToDiseases}
                className="rounded-full border border-outline-variant/50 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-on-surface-variant transition hover:border-primary hover:text-primary"
              >
                Change disease
              </button>
              <button
                onClick={resetToPlants}
                className="rounded-full border border-outline-variant/50 px-4 py-2 text-xs font-semibold uppercase tracking-wider text-on-surface-variant transition hover:border-primary hover:text-primary"
              >
                Change plant
              </button>
              <span className="text-on-surface-variant">{selectedPlantLabel} • {selectedDisease}</span>
            </div>

            <div className="flex items-center justify-between border-b border-surface-variant bg-surface/80 px-6 py-4 backdrop-blur-md">
              <div className="flex items-center gap-3">
                <span className="material-symbols-outlined text-primary" style={{ fontVariationSettings: "'FILL' 1" }}>
                  psychology
                </span>
                <h2 className="text-lg font-black">Assistant - {selectedDisease} ({selectedPlantLabel})</h2>
              </div>
              <button className="text-outline transition hover:text-primary">
                <span className="material-symbols-outlined">more_vert</span>
              </button>
            </div>

            <div ref={scrollRef} className="flex-1 space-y-6 overflow-y-auto bg-surface-container-low p-6 hide-scrollbar">
              {messages.map((message) => (
                <ChatBubble key={message.id} message={message} />
              ))}
              {loading && <TypingIndicator />}
            </div>

            <div className="border-t border-surface-variant bg-surface p-4">
              <div className="relative flex items-center">
                <button className="absolute left-3 text-outline transition hover:text-primary">
                  <span className="material-symbols-outlined">attach_file</span>
                </button>
                <input
                  value={draft}
                  onChange={(e) => setDraft(e.target.value)}
                  onKeyDown={handleKeyDown}
                  placeholder={`Ask about ${selectedDisease}...`}
                  className="w-full rounded-full border border-outline-variant/40 bg-surface-container px-12 py-3 text-sm outline-none focus:ring-2 focus:ring-primary"
                />
                <button
                  onClick={handleSend}
                  disabled={loading || !draft.trim()}
                  className="absolute right-2 rounded-full bg-primary p-2 text-white shadow-sm transition hover:bg-primary-container disabled:opacity-50"
                >
                  <span className="material-symbols-outlined" style={{ fontVariationSettings: "'FILL' 1" }}>
                    send
                  </span>
                </button>
              </div>
              <p className="mt-3 text-center text-xs text-outline">Botanical AI can make mistakes. Verify important agricultural advice.</p>
            </div>
            </motion.div>
          ) : null}
        </AnimatePresence>
      </Layout>
    </PageTransition>
  );
}