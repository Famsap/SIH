"use client";

import React, { useState } from "react";
import Link from "next/link";
import { useRouter } from "next/navigation";
import { Logo } from "@/components/landing/Logo";

export default function LoginPage() {
  const router = useRouter();
  const [email, setEmail] = useState("");
  const [password, setPassword] = useState("");
  const [showPassword, setShowPassword] = useState(false);
  const [rememberMe, setRememberMe] = useState(true);
  const [isLoading, setIsLoading] = useState(false);
  const [errorMessage, setErrorMessage] = useState("");

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    setErrorMessage("");

    if (!email || !password) {
      setErrorMessage("Please enter both email and password.");
      return;
    }

    setIsLoading(true);
    setTimeout(() => {
      setIsLoading(false);
      router.push("/chat");
    }, 800);
  };

  return (
    <div className="relative flex min-h-screen flex-col justify-center bg-paper px-4 py-12 sm:px-6 lg:px-8">
      <div className="absolute top-6 left-6 sm:left-10">
        <Logo />
      </div>

      <div className="sm:mx-auto sm:w-full sm:max-w-md">
        <div className="text-center">
          <h2 className="font-display text-3xl font-bold tracking-tight text-navy sm:text-4xl">
            Welcome back
          </h2>
          <p className="mt-2 text-sm text-ink/70">
            Sign in to access your saved IS standards & AI assistant.
          </p>
        </div>

        <div className="mt-8 rounded-2xl border border-line bg-white/80 p-8 shadow-xl backdrop-blur-md">
          {errorMessage && (
            <div className="mb-5 rounded-lg border border-red-200 bg-red-50 p-3 text-xs font-medium text-red-700">
              ⚠️ {errorMessage}
            </div>
          )}

          <form className="space-y-4" onSubmit={handleSubmit}>
            <div>
              <label htmlFor="email" className="block text-xs font-semibold uppercase tracking-wider text-ink/80">
                Email / Username
              </label>
              <input
                id="email"
                type="text"
                required
                value={email}
                onChange={(e) => setEmail(e.target.value)}
                placeholder="name@organization.gov.in"
                className="mt-1 w-full rounded-xl border border-line bg-paper/50 px-4 py-2.5 text-sm text-ink focus:border-saffron focus:bg-white focus:outline-none"
              />
            </div>

            <div>
              <div className="flex items-center justify-between">
                <label htmlFor="password" className="block text-xs font-semibold uppercase tracking-wider text-ink/80">
                  Password
                </label>
                <a href="#forgot" onClick={(e) => { e.preventDefault(); alert("Password reset link sent."); }} className="text-xs text-saffron-deep hover:underline">
                  Forgot?
                </a>
              </div>
              <div className="relative mt-1">
                <input
                  id="password"
                  type={showPassword ? "text" : "password"}
                  required
                  value={password}
                  onChange={(e) => setPassword(e.target.value)}
                  placeholder="••••••••"
                  className="w-full rounded-xl border border-line bg-paper/50 px-4 py-2.5 text-sm text-ink focus:border-saffron focus:bg-white focus:outline-none"
                />
                <button type="button" onClick={() => setShowPassword(!showPassword)} className="absolute right-3.5 top-1/2 -translate-y-1/2 text-xs font-semibold text-mist">
                  {showPassword ? "Hide" : "Show"}
                </button>
              </div>
            </div>

            <div className="flex items-center gap-2">
              <input type="checkbox" id="remember" checked={rememberMe} onChange={(e) => setRememberMe(e.target.checked)} className="h-4 w-4 rounded border-line text-saffron" />
              <label htmlFor="remember" className="text-xs text-ink/80 cursor-pointer">Remember me for 30 days</label>
            </div>

            <button type="submit" disabled={isLoading} className="btn-primary w-full rounded-xl py-2.5 text-sm font-semibold text-white shadow-md disabled:opacity-60">
              {isLoading ? "Signing in..." : "Sign In"}
            </button>
          </form>

          <div className="relative my-5 text-center text-xs text-mist uppercase tracking-wider">
            <span className="bg-white px-2">Or continue with</span>
          </div>

          <div className="grid grid-cols-2 gap-3">
            <button type="button" onClick={() => router.push("/chat")} className="rounded-xl border border-line bg-white py-2 text-xs font-semibold hover:bg-paper/40">
              🇮🇳 e-Pramaan
            </button>
            <button type="button" onClick={() => router.push("/chat")} className="rounded-xl border border-line bg-white py-2 text-xs font-semibold hover:bg-paper/40">
              Google
            </button>
          </div>
        </div>

        <p className="mt-6 text-center text-xs text-ink/70">
          Don&apos;t have an account?{" "}
          <Link href="/chat" className="font-semibold text-saffron-deep hover:underline">
            Continue as Guest
          </Link>
        </p>
      </div>
    </div>
  );
}
