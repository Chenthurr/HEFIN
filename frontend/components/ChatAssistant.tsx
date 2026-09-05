"use client";

import { FormEvent, useEffect, useRef, useState } from "react";
import { apiFetch } from "@/lib/api";

type Message = { id: string; role: "user" | "assistant"; content: string; route?: string; citations?: string[] };
const suggestions = ["What does an elevated HbA1c mean?", "Any recent trials on GLP-1 for weight loss?", "How do I file an insurance claim appeal?", "Do I have diabetes?"];
const routeLabels: Record<string, string> = { medical: "Medical Agent", research: "Research Agent", finance: "Finance Agent", safety_gate: "Safety Gate — Section 19" };

export default function ChatAssistant({ token }: { token: string }) {
  const [messages, setMessages] = useState<Message[]>([{ id: "welcome", role: "assistant", content: "Hi — ask me a health, research, or insurance question. I’ll retrieve grounded evidence, show the agent that handled it, and cite the sources used.", route: "medical", citations: [] }]);
  const [input, setInput] = useState("");
  const [busy, setBusy] = useState(false);
  const logRef = useRef<HTMLDivElement>(null);
  useEffect(() => { logRef.current?.scrollTo({ top: logRef.current.scrollHeight, behavior: "smooth" }); }, [messages, busy]);

  async function send(text = input) {
    const value = text.trim(); if (!value || busy) return;
    setInput(""); setMessages((m) => [...m, { id: crypto.randomUUID(), role: "user", content: value }]); setBusy(true);
    try {
      const result = await apiFetch<{ answer: string; citations: string[]; route: string }>("/api/v1/chat", { method: "POST", token, body: JSON.stringify({ message: value }) });
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: result.answer, route: result.route, citations: result.citations }]);
    } catch (error) {
      setMessages((m) => [...m, { id: crypto.randomUUID(), role: "assistant", content: error instanceof Error ? error.message : "The assistant could not complete that request.", route: "safety_gate", citations: [] }]);
    } finally { setBusy(false); }
  }
  function onSubmit(e: FormEvent) { e.preventDefault(); void send(); }
  return <div className="flex min-h-0 flex-1 flex-col">
    <div ref={logRef} className="min-h-0 flex-1 space-y-5 overflow-y-auto pr-2">
      {messages.map((message) => <div key={message.id} className={`flex ${message.role === "user" ? "justify-end" : "justify-start"}`}><div className="max-w-[86%]">
        {message.role === "assistant" && message.route && <div className="mb-2 flex items-center gap-2 font-mono text-[10px] uppercase tracking-[0.16em] text-[var(--muted)]"><span className={`h-1.5 w-1.5 rounded-full ${message.route === "finance" ? "bg-[var(--accent-amber)]" : message.route === "research" ? "bg-[#8b7fd6]" : message.route === "safety_gate" ? "bg-[#e05252]" : "bg-[var(--accent-teal)]"}`} />{routeLabels[message.route] ?? message.route}</div>}
        <div className={`rounded-2xl px-4 py-3 text-sm leading-7 ${message.role === "user" ? "rounded-br-md bg-[var(--accent-teal)] text-[#0b1220]" : "rounded-bl-md border border-[var(--border)] bg-[var(--surface-2)]"}`}>{message.content}{message.citations && message.citations.length > 0 && <div className="mt-3 flex flex-wrap gap-2 border-t border-[var(--border)] pt-3">{message.citations.map((citation) => <span key={citation} className="rounded-full border border-[var(--border)] px-2.5 py-1 font-mono text-[10px] text-[var(--muted)]">{citation}</span>)}</div>}</div>
      </div></div>)}
      {busy && <div className="flex justify-start"><div className="rounded-2xl rounded-bl-md border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3"><span className="inline-flex gap-1">{[0,1,2].map((i) => <span key={i} className="h-1.5 w-1.5 animate-pulse rounded-full bg-[var(--muted)]" style={{ animationDelay: `${i * 150}ms` }} />)}</span></div></div>}
    </div>
    <div className="pt-4">{!busy && messages.length < 3 && <div className="mb-3 flex flex-wrap gap-2">{suggestions.map((s) => <button key={s} onClick={() => void send(s)} className="rounded-full border border-[var(--border)] px-3 py-1.5 text-xs text-[var(--muted)] transition hover:border-[var(--accent-teal)] hover:text-[var(--foreground)]">{s}</button>)}</div>}
      <form onSubmit={onSubmit} className="flex gap-2 border-t border-[var(--border)] pt-4"><input value={input} onChange={(e) => setInput(e.target.value)} disabled={busy} placeholder="Ask HEFIN a question…" className="min-w-0 flex-1 rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-sm outline-none transition focus:border-[var(--accent-teal)]" /><button disabled={busy || !input.trim()} className="rounded-xl bg-[var(--accent-teal)] px-5 text-sm font-semibold text-[#0b1220] transition hover:brightness-110 disabled:cursor-not-allowed disabled:opacity-40">{busy ? "…" : "Send"}</button></form>
    </div>
  </div>;
}
