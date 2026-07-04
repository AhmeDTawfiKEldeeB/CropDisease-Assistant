import { Link } from "react-router-dom";
import PageTransition from "../components/PageTransition";
import { imageUrls } from "../data/mockData";

export default function LandingPage() {
  return (
    <PageTransition>
      <div className="min-h-screen bg-[#f7f8f3] text-[#122017]">
        <nav className="fixed inset-x-0 top-0 z-50 border-b border-black/5 bg-[#f7f8f3]/92 backdrop-blur-xl">
          <div className="mx-auto flex max-w-7xl items-center justify-between px-4 py-4 sm:px-6 lg:px-8">
            <Link to="/" className="flex items-center gap-2 text-[18px] font-semibold tracking-tight text-[#122017]">
              <span className="inline-flex h-8 w-8 items-center justify-center rounded-full bg-[#235f34] text-white">
                <span className="material-symbols-outlined text-[20px]">eco</span>
              </span>
              <span>Digital Greenhouse</span>
            </Link>

            <Link
              to="/workspace"
              className="inline-flex items-center justify-center rounded-2xl bg-gradient-to-b from-[#235f34] to-[#183f26] px-6 py-3 text-[15px] font-semibold text-white shadow-[0_18px_35px_rgba(24,63,38,0.28)] transition hover:-translate-y-0.5 hover:shadow-[0_22px_40px_rgba(24,63,38,0.34)]"
            >
              Get Started
            </Link>
          </div>
        </nav>

        <main className="mx-auto max-w-7xl px-4 pt-24 sm:px-6 lg:px-8">
          <section className="relative overflow-hidden pb-18 pt-6 lg:pb-24 lg:pt-12">
            <div className="absolute left-[-6rem] top-10 h-[26rem] w-[26rem] rounded-full bg-[#235f34]/14 blur-3xl" />
            <div className="absolute right-0 top-20 h-[18rem] w-[18rem] rounded-full bg-[#235f34]/10 blur-3xl" />

            <div className="relative grid items-center gap-12 lg:grid-cols-[1fr_1.02fr] lg:gap-16">
              <div className="max-w-2xl">
                <div className="inline-flex items-center rounded-full bg-[#235f34] px-4 py-2 text-[12px] font-medium uppercase tracking-[0.16em] text-white shadow-sm">
                  AI Plant Disease Diagnosis
                </div>

                <h1 className="mt-7 text-[clamp(3.5rem,8vw,5.8rem)] font-semibold leading-[0.94] tracking-[-0.06em] text-[#112017]">
                  Diagnose.
                  <br />
                  Understand.
                  <br />
                  <span className="text-[#235f34]">Protect.</span>
                </h1>

                <p className="mt-8 max-w-xl text-[18px] leading-8 text-[#415048] sm:text-[19px]">
                  Upload a clear image of your plant and get an instant AI diagnosis with expert-backed guidance.
                </p>

                <div className="mt-10 flex flex-col gap-4 sm:flex-row sm:items-center">
                  <Link
                    to="/workspace"
                    className="inline-flex items-center justify-center gap-3 rounded-2xl bg-gradient-to-b from-[#224f34] to-[#153522] px-8 py-4 text-[16px] font-medium text-white shadow-[0_18px_30px_rgba(21,53,34,0.28)] transition hover:-translate-y-0.5"
                  >
                    <span className="material-symbols-outlined text-[20px]">upload</span>
                    Start Diagnosis
                  </Link>
                </div>
              </div>

              <div className="relative flex justify-center lg:justify-end">
                <div className="absolute inset-x-8 bottom-[-1.5rem] h-28 rounded-full bg-black/8 blur-3xl" />
                <div className="relative w-full max-w-[680px] overflow-hidden rounded-[3rem]">
                  <img
                    src={imageUrls.hero}
                    alt="Disease-affected leaf close up"
                    className="h-[560px] w-full object-cover object-center sm:h-[680px]"
                  />
                  <div className="pointer-events-none absolute inset-0 bg-gradient-to-br from-white/8 via-transparent to-black/10" />
                </div>
              </div>
            </div>
          </section>

          <section id="how-it-works" className="pb-20 pt-10 lg:pb-28 lg:pt-16">
            <h2 className="text-center text-[clamp(2rem,4vw,3.25rem)] font-medium tracking-[-0.05em] text-[#122017]">
              How it works
            </h2>

            <div className="mt-12 grid gap-8 md:grid-cols-3 md:gap-6 lg:mt-16 lg:gap-10">
              <div className="flex items-start gap-5">
                <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-[#235f34] text-white shadow-sm">
                  <span className="material-symbols-outlined text-[32px]">photo_camera</span>
                </div>
                <div>
                  <p className="text-[16px] font-semibold text-[#122017]">1. Upload Image</p>
                  <p className="mt-2 max-w-[15rem] text-[15px] leading-7 text-[#55655c]">Take or upload a clear photo of the affected leaf.</p>
                </div>
                <span className="hidden pt-6 text-[28px] text-[#122017]/80 md:block">→</span>
              </div>

              <div className="flex items-start gap-5">
                <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-[#235f34] text-white shadow-sm">
                  <span className="material-symbols-outlined text-[32px]">scan</span>
                </div>
                <div>
                  <p className="text-[16px] font-semibold text-[#122017]">2. AI Analysis</p>
                  <p className="mt-2 max-w-[15rem] text-[15px] leading-7 text-[#55655c]">Our AI analyzes the image to detect the disease.</p>
                </div>
                <span className="hidden pt-6 text-[28px] text-[#122017]/80 md:block">→</span>
              </div>

              <div className="flex items-start gap-5">
                <div className="flex h-20 w-20 shrink-0 items-center justify-center rounded-full bg-[#235f34] text-white shadow-sm">
                  <span className="material-symbols-outlined text-[32px]">sms</span>
                </div>
                <div>
                  <p className="text-[16px] font-semibold text-[#122017]">3. Get Guidance</p>
                  <p className="mt-2 max-w-[15rem] text-[15px] leading-7 text-[#55655c]">Receive the diagnosis and recommended treatments.</p>
                </div>
              </div>
            </div>
          </section>

          <section id="assistant" className="pb-20 lg:pb-28">
            <div className="relative overflow-hidden rounded-[2rem] bg-[#062014] shadow-[0_28px_70px_rgba(6,32,20,0.25)]">
              <div className="absolute inset-0 bg-[radial-gradient(circle_at_80%_45%,rgba(118,194,119,0.14),transparent_25%),radial-gradient(circle_at_78%_50%,rgba(118,194,119,0.12),transparent_34%)]" />
              <div className="grid min-h-[360px] items-center gap-8 px-6 py-8 sm:px-10 lg:grid-cols-[0.95fr_1.15fr_0.55fr] lg:px-12 lg:py-10">
                <div className="relative overflow-hidden rounded-[1.75rem]">
                  <img
                    src={imageUrls.leaf}
                    alt="Healthy green plant leaves"
                    className="h-full min-h-[280px] w-full object-cover object-center"
                  />
                  <div className="absolute inset-0 bg-gradient-to-tr from-black/30 via-transparent to-transparent" />
                </div>

                <div className="relative max-w-xl text-white">
                  <p className="text-[12px] font-medium uppercase tracking-[0.24em] text-[#8fc893]">AI Assistant</p>
                  <h3 className="mt-4 text-[clamp(2rem,4vw,3.15rem)] font-medium leading-[1.08] tracking-[-0.05em] text-white">
                    Have questions about a disease?
                  </h3>
                  <p className="mt-5 max-w-lg text-[17px] leading-8 text-white/78">
                    Chat with our AI assistant to understand the cause, symptoms, and best treatment for your plant.
                  </p>
                  <Link
                    to="/assistant"
                    className="mt-8 inline-flex items-center justify-center gap-3 rounded-full border border-white/18 bg-transparent px-7 py-4 text-[16px] font-medium text-white transition hover:border-[#8fc893]/45 hover:bg-white/5"
                  >
                    <span className="material-symbols-outlined text-[20px]">chat_bubble</span>
                    Open Assistant
                  </Link>
                </div>

                <div className="relative hidden items-center justify-center lg:flex">
                  <div className="absolute h-44 w-44 rounded-full border border-white/10" />
                  <div className="absolute h-32 w-32 rounded-full border border-white/10" />
                  <div className="flex h-28 w-28 items-center justify-center rounded-full border-4 border-[#235f34] text-[#235f34]">
                    <span className="material-symbols-outlined text-[54px]">forum</span>
                  </div>
                </div>
              </div>
            </div>
          </section>
        </main>
      </div>
    </PageTransition>
  );
}