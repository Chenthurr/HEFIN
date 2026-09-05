"use client";

import { FormEvent, useState } from "react";
import { apiFetch } from "@/lib/api";

type Props = { onAuthenticated: (token: string) => void };

export default function AuthPanel({ onAuthenticated }: Props) {
  const [mode, setMode] = useState<"login" | "register">("login");
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [name, setName] = useState("");
  const [error, setError] = useState("");
  const [busy, setBusy] = useState(false);

  async function submit(e: FormEvent) {
    e.preventDefault();
    setError("");
    setBusy(true);
    try {
      if (mode === "register") {
        await apiFetch("/api/v1/auth/register", {
          method: "POST",
          body: JSON.stringify({ email, password, full_name: name || null, role: "patient", preferred_language: "en" }),
        });
      }
      const result = await apiFetch<{ access_token: string }>("/api/v1/auth/login", {
        method: "POST", body: JSON.stringify({ email, password }),
      });
      localStorage.setItem("hefin_access_token", result.access_token);
      onAuthenticated(result.access_token);
    } catch (err) {
      setError(err instanceof Error ? err.message.replace(/^API error \d+: /, "") : "Authentication failed.");
    } finally { setBusy(false); }
  }

  return (
    <div className="mx-auto w-full max-w-md rounded-2xl border border-[var(--border)] bg-[var(--surface)]/90 p-7 shadow-2xl backdrop-blur">
      <p className="mb-2 font-mono text-[10px] uppercase tracking-[0.25em] text-[var(--accent-teal)]">Secure access</p>
      <h2 className="mb-2 font-serif text-2xl">{mode === "login" ? "Welcome back" : "Create your HEFIN account"}</h2>
      <p className="mb-6 text-sm leading-6 text-[var(--muted)]">Your account controls access to chat and personal documents.</p>
      <form onSubmit={submit} className="space-y-3">
        {mode === "register" && <input value={name} onChange={(e) => setName(e.target.value)} placeholder="Full name" className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-sm outline-none focus:border-[var(--accent-teal)]" />}
        <input required type="email" value={email} onChange={(e) => setEmail(e.target.value)} placeholder="Email" className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-sm outline-none focus:border-[var(--accent-teal)]" />
        <input required minLength={8} type="password" value={password} onChange={(e) => setPassword(e.target.value)} placeholder="Password (8+ characters)" className="w-full rounded-xl border border-[var(--border)] bg-[var(--surface-2)] px-4 py-3 text-sm outline-none focus:border-[var(--accent-teal)]" />
        {error && <div className="rounded-xl border border-red-400/30 bg-red-400/5 p-3 text-xs leading-5 text-red-200">{error}</div>}
        <button disabled={busy} className="w-full rounded-xl bg-[var(--accent-amber)] px-4 py-3 text-sm font-semibold text-[var(--background)] disabled:opacity-50">{busy ? "Working…" : mode === "login" ? "Sign in" : "Create account"}</button>
      </form>
      <button onClick={() => { setMode(mode === "login" ? "register" : "login"); setError(""); }} className="mt-5 w-full text-xs text-[var(--muted)] hover:text-[var(--foreground)]">{mode === "login" ? "Need an account? Register" : "Already registered? Sign in"}</button>
    </div>
  );
}
