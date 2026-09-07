import Link from "next/link";

/** Placeholder until the chat UI is scaffolded. Landing CTAs already point here. */
export default function ChatPlaceholder() {
  return (
    <main className="flex min-h-screen flex-col items-center justify-center bg-paper px-6 text-center">
      <p className="font-mono text-[11px] uppercase tracking-[0.22em] text-saffron-deep">
        Assistant
      </p>
      <h1 className="mt-3 font-display text-3xl font-semibold text-navy sm:text-4xl">
        Chat is next.
      </h1>
      <p className="mt-3 max-w-md text-sm leading-relaxed text-ink/70">
        The landing page is live. The RAG-backed chat UI will land once the
        backend is scaffolded.
      </p>
      <Link
        href="/"
        className="btn-primary mt-8 rounded-full px-6 py-3 text-sm font-semibold text-white"
      >
        Back to home
      </Link>
    </main>
  );
}
