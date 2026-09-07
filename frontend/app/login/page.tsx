"use client";

import Link from "next/link";
import { FormEvent, useState } from "react";
import { Logo } from "@/components/landing/Logo";

export default function LoginPage() {
  const [submitted, setSubmitted] = useState(false);

  function handleSubmit(event: FormEvent<HTMLFormElement>) {
    event.preventDefault();
    setSubmitted(true);
  }

  return (
    <main className="relative min-h-screen overflow-hidden bg-paper">
      <div className="absolute inset-y-0 left-0 hidden w-[42%] bg-navy lg:block" />
      <div className="relative mx-auto grid min-h-screen max-w-[1440px] lg:grid-cols-[42%_58%]">
        <section className="relative hidden overflow-hidden px-10 py-10 text-paper lg:flex lg:flex-col lg:justify-between xl:px-16">
          <div className="absolute -left-24 top-24 h-72 w-72 rounded-full border border-white/10" />
          <div className="absolute -bottom-28 right-[-5rem] h-96 w-96 rounded-full border border-saffron/30" />
          <div className="absolute left-[18%] top-[42%] h-32 w-32 rotate-45 border border-gold/30" />

          <div className="relative z-10">
            <Logo inverted />
          </div>

          <div className="relative z-10 max-w-md pb-8 xl:pb-16">
            <p className="font-mono text-[11px] uppercase tracking-[0.28em] text-saffron">
              Your standards desk
            </p>
            <h1 className="mt-5 font-display text-5xl font-semibold leading-[1.05] tracking-[-0.03em] xl:text-6xl">
              Clarity for every code.
            </h1>
            <p className="mt-6 max-w-sm text-[15px] leading-7 text-paper/65">
              Keep your questions, references, and compliance work close at hand with ManakSetu.
            </p>
            <div className="mt-12 flex items-center gap-3 text-xs text-paper/45">
              <span className="h-px w-10 bg-saffron" />
              Grounded in official BIS text
            </div>
          </div>

          <p className="relative z-10 font-mono text-[10px] uppercase tracking-[0.2em] text-paper/35">
            IS codes · made navigable
          </p>
        </section>

        <section className="flex min-h-screen flex-col px-5 py-7 sm:px-10 sm:py-10 lg:px-16 xl:px-24">
          <div className="flex items-center justify-between lg:justify-end">
            <div className="lg:hidden">
              <Logo />
            </div>
            <p className="text-sm text-ink/55">
              New to ManakSetu?{" "}
              <Link href="/" className="font-semibold text-saffron-deep hover:text-navy">
                Explore first
              </Link>
            </p>
          </div>

          <div className="flex flex-1 items-center justify-center py-14 lg:justify-start lg:py-20">
            <div className="w-full max-w-[430px]">
              <p className="font-mono text-[11px] uppercase tracking-[0.25em] text-saffron-deep">
                Welcome back
              </p>
              <h2 className="mt-4 font-display text-4xl font-semibold tracking-[-0.03em] text-navy sm:text-5xl">
                Sign in to your desk.
              </h2>
              <p className="mt-4 text-[15px] leading-7 text-ink/60">
                Pick up where you left off with your standards research.
              </p>

              <form onSubmit={handleSubmit} className="mt-10 space-y-5">
                <div>
                  <label htmlFor="email" className="mb-2 block text-xs font-bold uppercase tracking-[0.16em] text-ink/65">
                    Work email
                  </label>
                  <input
                    id="email"
                    name="email"
                    type="email"
                    autoComplete="email"
                    placeholder="you@organisation.com"
                    required
                    className="h-14 w-full rounded-xl border border-ink/15 bg-white/55 px-4 text-sm text-navy outline-none transition placeholder:text-ink/30 focus:border-saffron focus:ring-4 focus:ring-saffron/10"
                  />
                </div>
                <div>
                  <div className="mb-2 flex items-center justify-between">
                    <label htmlFor="password" className="block text-xs font-bold uppercase tracking-[0.16em] text-ink/65">
                      Password
                    </label>
                    <button type="button" className="text-xs font-semibold text-saffron-deep hover:text-navy">
                      Forgot password?
                    </button>
                  </div>
                  <input
                    id="password"
                    name="password"
                    type="password"
                    autoComplete="current-password"
                    placeholder="Enter your password"
                    required
                    minLength={8}
                    className="h-14 w-full rounded-xl border border-ink/15 bg-white/55 px-4 text-sm text-navy outline-none transition placeholder:text-ink/30 focus:border-saffron focus:ring-4 focus:ring-saffron/10"
                  />
                </div>
                <label className="flex items-center gap-3 text-sm text-ink/60">
                  <input type="checkbox" name="remember" className="h-4 w-4 accent-saffron" />
                  Keep me signed in
                </label>
                <button type="submit" className="btn-primary h-14 w-full rounded-xl text-sm font-bold text-white">
                  {submitted ? "Request received" : "Sign in to ManakSetu"}
                </button>
                {submitted && (
                  <p role="status" className="text-center text-xs text-teal">
                    Authentication will connect here when the account service is ready.
                  </p>
                )}
              </form>

              <div className="my-8 flex items-center gap-4 text-[10px] font-bold uppercase tracking-[0.2em] text-ink/30">
                <span className="h-px flex-1 bg-ink/10" />
                Secure workspace access
                <span className="h-px flex-1 bg-ink/10" />
              </div>
              <p className="text-center text-xs leading-6 text-ink/45">
                By continuing, you agree to use ManakSetu for responsible standards research.
              </p>
            </div>
          </div>

          <div className="flex justify-between border-t border-line pt-5 text-[10px] uppercase tracking-[0.16em] text-ink/35">
            <span>ManakSetu</span>
            <Link href="/" className="hover:text-navy">Back to home</Link>
          </div>
        </section>
      </div>
    </main>
  );
}
