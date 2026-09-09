import Link from "next/link";

const CONTACTS = [
  {
    label: "BIS toll-free helpline",
    value: "1800-11-7000",
    href: "tel:1800117000",
    detail: "For general consumer and standards-related assistance.",
  },
  {
    label: "BIS email",
    value: "info@bis.gov.in",
    href: "mailto:info@bis.gov.in",
    detail: "Share your question with the relevant BIS team.",
  },
];

const ROUTES = [
  {
    title: "Consumer complaint or product query",
    body: "Use BIS consumer services for complaints, product certification questions, and consumer guidance.",
    href: "https://www.bis.gov.in/consumer-overview/",
    action: "Open consumer services",
  },
  {
    title: "Office and department contacts",
    body: "Find the latest regional office details and department contacts on the official BIS contact page.",
    href: "https://www.bis.gov.in/contact-us/",
    action: "View BIS contacts",
  },
  {
    title: "Ask ManakSetu first",
    body: "Get a cited answer from the indexed BIS corpus for questions about IS codes, certification, and hallmarking.",
    href: "/chat",
    action: "Open assistant",
  },
];

export default function HelplinePage() {
  return (
    <main className="min-h-screen bg-paper px-5 py-8 text-ink sm:px-8 sm:py-12">
      <div className="mx-auto max-w-6xl">
        <header className="flex items-center justify-between gap-4">
          <Link href="/" className="font-display text-lg font-bold text-navy">
            ManakSetu
          </Link>
          <Link href="/" className="text-sm font-semibold text-ink/60 transition hover:text-navy">
            Back to home
          </Link>
        </header>

        <section className="relative mt-16 overflow-hidden rounded-[2rem] bg-navy px-6 py-10 text-paper shadow-[0_24px_70px_-30px_rgba(7,21,37,0.7)] sm:px-12 sm:py-14">
          <div className="orb -right-20 -top-28 h-72 w-72 bg-saffron/25" aria-hidden />
          <p className="relative font-mono text-[11px] uppercase tracking-[0.2em] text-gold">BIS support desk</p>
          <h1 className="relative mt-4 max-w-3xl font-display text-4xl leading-tight sm:text-6xl">
            Need a human answer?
          </h1>
          <p className="relative mt-5 max-w-xl text-sm leading-relaxed text-paper/70 sm:text-base">
            Start with the official BIS channels below. For standards and certification questions, ManakSetu can help you prepare a clearer query before you call or write.
          </p>
        </section>

        <section className="mt-8 grid gap-4 sm:grid-cols-2" aria-label="BIS helpline channels">
          {CONTACTS.map((contact) => (
            <a
              key={contact.label}
              href={contact.href}
              className="lift rounded-2xl border border-line bg-white p-6"
            >
              <p className="text-xs font-semibold uppercase tracking-[0.14em] text-teal">{contact.label}</p>
              <p className="mt-3 break-all font-display text-2xl font-semibold text-navy sm:text-3xl">{contact.value}</p>
              <p className="mt-2 text-sm leading-relaxed text-ink/60">{contact.detail}</p>
            </a>
          ))}
        </section>

        <section className="mt-14">
          <div className="flex flex-col justify-between gap-3 border-b border-line pb-5 sm:flex-row sm:items-end">
            <div>
              <p className="font-mono text-[11px] uppercase tracking-[0.2em] text-saffron-deep">Choose a route</p>
              <h2 className="mt-2 font-display text-3xl font-semibold text-navy">Get to the right place faster.</h2>
            </div>
            <p className="max-w-sm text-sm leading-relaxed text-ink/60">Official BIS pages can change. Always confirm current timings and contact details before sending sensitive information.</p>
          </div>
          <div className="mt-6 grid gap-4 md:grid-cols-3">
            {ROUTES.map((route, index) => (
              <article key={route.title} className="rounded-2xl border border-line bg-white p-6">
                <span className="font-mono text-xs text-saffron-deep">0{index + 1}</span>
                <h3 className="mt-8 font-display text-xl font-semibold text-navy">{route.title}</h3>
                <p className="mt-3 min-h-20 text-sm leading-relaxed text-ink/60">{route.body}</p>
                <Link
                  href={route.href}
                  target={route.href.startsWith("http") ? "_blank" : undefined}
                  rel={route.href.startsWith("http") ? "noreferrer" : undefined}
                  className="mt-6 inline-flex text-sm font-bold text-saffron-deep hover:text-navy"
                >
                  {route.action} <span aria-hidden className="ml-2">-&gt;</span>
                </Link>
              </article>
            ))}
          </div>
        </section>

        <p className="mt-12 border-t border-line pt-5 text-xs leading-relaxed text-ink/50">
          ManakSetu is not affiliated with BIS. It does not replace official advice, complaint registration, or emergency services. Use the official BIS website for the latest verified information.
        </p>
      </div>
    </main>
  );
}