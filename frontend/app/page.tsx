"use client";

import dynamic from "next/dynamic";
import { useState } from "react";
import ChatAssistant from "@/components/ChatAssistant";
import DocumentVault from "@/components/DocumentVault";

const MedicalGalaxyScene = dynamic(() => import("@/components/MedicalGalaxyScene"), { ssr: false });

type Screen = "landing" | "chat" | "vault";

export default function Home() {
  const [screen, setScreen] = useState<Screen>("chat");

  return (
    <main className="relative min-h-screen overflow-hidden bg-[var(--background)]">
      <div className="pointer-events-none fixed inset-0 opacity-70"><MedicalGalaxyScene /></div>
      <div className="pointer-events-none fixed inset-0 bg-[radial-gradient(circle_at_70%_35%,rgba(79,209,197,0.08),transparent_30%),linear-gradient(to_top,#0b1220,transparent,#0b1220)]" />

      <div className="relative z-10 flex min-h-screen flex-col">
        <header className="flex items-center justify-between px-6 py-6 md:px-10">
          <button onClick={() => setScreen("chat")} className="font-mono text-sm tracking-[0.2em] text-[var(--muted)]">
            <span className="text-[var(--foreground)]">HEFIN</span> · Healthcare Intelligence
          </button>
          <nav className="flex items-center gap-5 font-mono text-[10px] uppercase tracking-[0.18em] text-[var(--muted)]">
            <button onClick={() => setScreen("chat")} className="hover:text-[var(--foreground)]">AI Assistant</button>
            <button onClick={() => setScreen("vault")} className="hover:text-[var(--foreground)]">Document Vault</button>
          </nav>
        </header>

        {screen === "chat" && (
          <section className="flex min-h-0 flex-1 justify-center px-6 pb-8">
            <div className="flex min-h-0 w-full max-w-4xl flex-col rounded-2xl border border-[var(--border)] bg-[var(--surface)]/85 p-5 shadow-2xl backdrop-blur md:p-7">
              <div className="mb-5 border-b border-[var(--border)] pb-5">
                <h2 className="font-serif text-2xl">Ask HEFIN</h2>
                <p className="mt-1 text-xs text-[var(--muted)]">Grounded retrieval · specialist routing · safety gate</p>
              </div>
              <ChatAssistant />
            </div>
          </section>
        )}

        {screen === "vault" && (
          <section className="mx-auto w-full max-w-4xl flex-1 px-6 pb-12">
            <div className="mb-6">
              <h2 className="font-serif text-3xl">Document Vault</h2>
              <p className="mt-2 text-sm text-[var(--muted)]">Upload PDF/TXT reports. The backend extracts text and produces an educational summary through the safety-gated model path.</p>
            </div>
            <DocumentVault />
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
