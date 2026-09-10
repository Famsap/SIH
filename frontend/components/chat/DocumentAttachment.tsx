"use client";

import { DragEvent, useRef, useState } from "react";
import { DocumentReviewResult, reviewDocument } from "@/lib/api";

const MAX_FILE_SIZE = 3 * 1024 * 1024;
const ACCEPTED = ".pdf,.docx,.txt,.jpg,.jpeg,.png,.webp,.gif";

export function DocumentAttachment() {
  const inputRef = useRef<HTMLInputElement>(null);
  const [open, setOpen] = useState(false);
  const [dragging, setDragging] = useState(false);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState("");
  const [result, setResult] = useState<DocumentReviewResult | null>(null);

  const selectFile = async (file?: File) => {
    if (!file) return;
    setOpen(true);
    setError("");
    setResult(null);
    if (file.size > MAX_FILE_SIZE) {
      setError("This file is larger than 3 MB. Choose a smaller file.");
      return;
    }
    setLoading(true);
    try {
      setResult(await reviewDocument(file));
    } catch (reason) {
      setError(reason instanceof Error ? reason.message : "The document could not be reviewed.");
    } finally {
      setLoading(false);
    }
  };

  const onDrop = (event: DragEvent<HTMLDivElement>) => {
    event.preventDefault();
    setDragging(false);
    void selectFile(event.dataTransfer.files[0]);
  };

  return (
    <div className="relative shrink-0">
      {open && (
        <div className="absolute bottom-14 right-0 z-20 w-[min(360px,calc(100vw-2rem))] rounded-2xl border border-line bg-paper p-3 shadow-[0_18px_45px_-18px_rgba(7,21,37,0.35)]">
          <div
            role="button"
            tabIndex={0}
            onClick={() => inputRef.current?.click()}
            onKeyDown={(event) => { if (event.key === "Enter" || event.key === " ") inputRef.current?.click(); }}
            onDragOver={(event) => { event.preventDefault(); setDragging(true); }}
            onDragLeave={() => setDragging(false)}
            onDrop={onDrop}
            className={`cursor-pointer rounded-xl border border-dashed p-4 text-center transition ${dragging ? "border-saffron bg-saffron/10" : "border-saffron/40 bg-white hover:border-saffron"}`}
          >
            <p className="font-display text-lg font-semibold text-navy">Drop a file to review</p>
            <p className="mt-1 text-[11px] text-ink/55">PDF, DOCX, TXT, JPG, JPEG, PNG, WEBP, GIF</p>
            <p className="mt-2 font-mono text-[10px] uppercase tracking-[0.1em] text-saffron-deep">Maximum file size: 3 MB</p>
            <input ref={inputRef} type="file" accept={ACCEPTED} className="sr-only" onChange={(event) => void selectFile(event.target.files?.[0])} />
          </div>
          {loading && <p className="px-1 pt-3 text-xs text-teal">Preparing preliminary review...</p>}
          {error && <p className="mt-3 rounded-lg bg-red-50 px-3 py-2 text-xs text-red-700">{error}</p>}
          {result && (
            <div className="mt-3 max-h-64 overflow-y-auto rounded-xl border border-line bg-white p-3" aria-live="polite">
              <div className="flex items-start justify-between gap-2">
                <div><p className="font-mono text-[9px] uppercase tracking-[0.12em] text-teal">Preliminary review</p><p className="mt-1 break-all text-xs font-semibold text-navy">{result.filename}</p></div>
                <span className="shrink-0 rounded-full bg-gold/20 px-2 py-1 text-[9px] font-bold text-saffron-deep">Verify</span>
              </div>
              <div className="mt-3 grid gap-1.5">
                {result.checks.map((check) => <div key={check.label} className="rounded-lg bg-paper px-2.5 py-2"><p className={`text-[9px] font-bold uppercase tracking-[0.08em] ${check.status === "pass" ? "text-teal" : "text-saffron-deep"}`}>{check.status === "pass" ? "Detected" : "Check"} · {check.label}</p><p className="mt-0.5 text-[11px] leading-relaxed text-ink/65">{check.detail}</p></div>)}
              </div>
              <p className="mt-3 border-t border-line pt-3 text-[10px] leading-relaxed text-ink/50">{result.disclaimer}</p>
            </div>
          )}
        </div>
      )}
      <button type="button" onClick={() => setOpen((value) => !value)} aria-label="Review a document" aria-expanded={open} className={`grid h-11 w-11 place-items-center rounded-xl border text-lg transition ${open ? "border-saffron bg-saffron/10 text-saffron-deep" : "border-slate-200 bg-slate-50 text-slate-600 hover:border-saffron hover:text-saffron-deep"}`}>
        <span aria-hidden>📎</span>
      </button>
    </div>
  );
}