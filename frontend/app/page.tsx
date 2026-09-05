"use client";

import dynamic from "next/dynamic";
import { useEffect, useState } from "react";
import AuthPanel from "@/components/AuthPanel";
import ChatAssistant from "@/components/ChatAssistant";
import DocumentVault from "@/components/DocumentVault";

const MedicalGalaxyScene = dynamic(() => import("@/components/MedicalGalaxyScene"), { ssr: false });

type Screen = "landing" | "chat" | "vault" | "auth";

export default function Home() {
  const [screen, setScreen] = useState<Screen>("landing");
  const [token, setToken] = useState<string | null>(null);

  useEffect(() => {
    setToken(localStorage.getItem("hefin_access_token"));
  }, []);

  function openProtected(next: "chat" | "vault") {
    if (token) setScreen(next);
    else setScreen("auth");
  }

  function logout() {
    localStorage.removeItem("hefin_access_token");
    setToken(null);
    setScreen("landing");
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-[var(--background)]">
      <div className="pointer-events-none fixed inset-0 opacity-70"><MedicalGalaxyScene /></div>
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_70%_35%,rgba(79,209,197,0.08),transparent_30%),linear-gradient(to_top,#0b1220,transparent,#0b1220)]" />

      <div className="relative z-10 flex min-h-screen flex-col">
        <header className="flex items-center justify-between px-6 py-6 md:px-10">
          <button onClick={() => setScreen("landing")} className="font-mono text-sm tracking-[0.2em] text-[var(--muted)]">
            <span className="text-[var(--foreground)]">HEFIN</span> · Healthcare Intelligence
          </button>
          <nav className="flex items-center gap-5 font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--muted)]">
            <button onClick={() => setScreen("landing")} className="hover:text-[var(--foreground)]">Platform</button>
            <button onClick={() => openProtected("chat")} className="hover:text-[var(--foreground)]">AI Assistant</button>
            <button onClick={() => openProtected("vault")} className="hover:text-[var(--foreground)]">Document Vault</button>
            {token ? <button onClick={logout} className="hover:text-[var(--foreground)]">Sign out</button> : <button onClick={() => setScreen("auth")} className="hover:text-[var(--foreground)]">Sign in</button>}
          </nav>
        </header>

        {screen === "landing" && (
          <section className="flex flex-1 items-center px-6 py-10 md:px-16">
            <div className="max-w-2xl">
              <p className="mb-5 font-mono text-xs uppercase tracking-[0.3em] text-[var(--accent-teal)]">Healthcare Financial Intelligence Network</p>
              <h1 className="mb-6 text-5xl leading-[1.04] md:text-7xl" style={{ fontFamily: "Fraunces, Georgia, serif" }}>
                Every scattered<br />record, one<br /><span className="text-[var(--accent-teal)]">connected</span> layer.
              </h1>
              <p className="mb-8 max-w-xl text-sm leading-7 text-[var(--muted)] md:text-base">
                Ask questions across healthcare, research and insurance. HEFIN retrieves evidence, routes the request to a specialist agent, applies a safety gate, and returns cited answers.
              </p>
              <div className="flex flex-wrap gap-3">
                <button onClick={() => openProtected("chat")} className="rounded-full bg-[var(--accent-amber)] px-6 py-3 text-sm font-medium text-[var(--background)] hover:brightness-110">Try the AI Assistant →</button>
                <button onClick={() => openProtected("vault")} className="rounded-full border border-[var(--border)] bg-[var(--surface)]/50 px-6 py-3 text-sm hover:border-[var(--foreground)]">Open Document Vault</button>
              </div>
              <div className="mt-16 grid max-w-2xl gap-3 sm:grid-cols-3">
                {[
                  ["01", "RAG", "Retrieval before generation, with citations"],
                  ["02", "Multilingual", "Target architecture includes 10 languages"],
                  ["03", "Safety", "Education, never autonomous diagnosis"],
                ].map(([n, t, d]) => (
                  <div key={n} className="rounded-xl border border-[var(--border)] bg-[var(--surface)]/60 p-4 backdrop-blur">
                    <div className="font-mono text-[10px] text-[var(--accent-teal)]">{n} · {t}</div>
                    <div className="mt-2 text-xs leading-5 text-[var(--muted)]">{d}</div>
                  </div>
                ))}
              </div>
            </div>
          </section>
        )}

        {screen === "auth" && (
          <section className="flex flex-1 items-center justify-center px-6 py-10">
            <AuthPanel onAuthenticated={(t) => { setToken(t); setScreen("chat"); }} />
          </section>
        )}

        {screen === "chat" && token && (
          <section className="flex min-h-0 flex-1 justify-center px-6 pb-8">
            <div className="flex min-h-0 w-full max-w-4xl flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface)]/85 p-5 shadow-2xl backdrop-blur md:p-7">
              <div className="mb-5 border-b border-[var(--border)] pb-5">
                <h2 className="font-serif text-2xl">Ask HEFIN</h2>
                <p className="mt-1 text-xs text-[var(--muted)]">Grounded retrieval · specialist routing · safety gate</p>
              </div>
              <ChatAssistant token={token} />
            </div>
          </section>
        )}

        {screen === "vault" && token && (
          <section className="mx-auto w-full max-w-4xl flex-1 px-6 pb-12">
            <div className="mb-6">
              <h2 className="font-serif text-3xl">Document Vault</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">Upload PDF/TXT reports. The backend extracts text and produces an educational summary through the safety-gated model path.</p>
            </div>
            <DocumentVault token={token} />
          </section>
        )}

        <footer className="flex justify-between px-6 py-5 font-mono text-[10px] text-[var(--muted)] md:px-10">
          <span>Evidence-grounded · citation-backed</span>
          <span>HEFIN v0.1</span>
        </footer>
      </div>
    </main>
  );
}
