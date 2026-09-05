"use client";

import { ChangeEvent, useEffect, useState } from "react";
import { apiFetch } from "@/lib/api";

type Doc = { id: string; filename: string; content_type: string; status: string; summary?: string | null };

export default function DocumentVault({ token }: { token: string }) {
  const [docs, setDocs] = useState<Doc[]>([]);
  const [busy, setBusy] = useState(false);
  const [error, setError] = useState("");

  async function refresh() {
    try { setDocs(await apiFetch<Doc[]>("/api/v1/documents", { token })); }
    catch (e) { setError(e instanceof Error ? e.message : "Could not load documents."); }
  }
  useEffect(() => { void refresh(); }, []);

  async function upload(e: ChangeEvent<HTMLInputElement>) {
    const file = e.target.files?.[0]; if (!file) return;
    setBusy(true); setError("");
    try {
      const form = new FormData(); form.append("file", file);
      const base = process.env.NEXT_PUBLIC_API_URL || "http://localhost:8000";
      const res = await fetch(`${base}/api/v1/documents/upload`, { method: "POST", headers: { Authorization: `Bearer ${token}` }, body: form });
      if (!res.ok) throw new Error(await res.text());
      const uploaded = await res.json() as Doc;
      const parsed = await apiFetch<Doc>(`/api/v1/documents/${uploaded.id}/parse`, { method: "POST", token, body: JSON.stringify({}) });
      setDocs((d) => [parsed, ...d]);
    } catch (e) { setError(e instanceof Error ? e.message : "Upload failed."); }
    finally { setBusy(false); e.target.value = ""; }
  }

  return (
    <div className="space-y-5">
      <label className="block cursor-pointer rounded-2xl border border-dashed border-[var(--border)] bg-[var(--surface)] p-8 text-center transition hover:border-[var(--accent-teal)]">
        <input type="file" accept=".pdf,.txt,application/pdf,text/plain" onChange={upload} className="hidden" disabled={busy} />
        <div className="mb-2 text-3xl text-[var(--accent-teal)]">↑</div>
        <div className="text-sm">{busy ? "Uploading and parsing…" : "Upload a medical report"}</div>
        <div className="mt-1 font-mono text-[10px] text-[var(--muted)]">PDF or TXT · extracted and summarized by the backend</div>
      </label>
      {error && <div className="rounded-xl border border-red-400/30 p-3 text-xs text-red-200">{error}</div>}
      {docs.length === 0 ? <div className="rounded-2xl border border-[var(--border)] bg-[var(--surface)] p-6 text-sm text-[var(--muted)]">No documents yet.</div> : docs.map((doc) => (
        <article key={doc.id} className="rounded-2xl border border-[var(--border)] bg-[var(--surface-2)] p-5">
          <div className="flex items-center justify-between gap-4"><div className="truncate text-sm">{doc.filename}</div><span className="rounded-full border border-[var(--border)] px-2.5 py-1 font-mono text-[10px] uppercase tracking-wider text-[var(--accent-teal)]">{doc.status}</span></div>
          {doc.summary && <p className="mt-4 border-t border-[var(--border)] pt-4 text-sm leading-7 text-[var(--muted)]">{doc.summary}</p>}
        </article>
      ))}
    </div>
  );
}
