import { Navbar } from "@/components/landing/Navbar";
import { Hero } from "@/components/landing/Hero";
import { Marquee } from "@/components/landing/Marquee";
import { Features } from "@/components/landing/Features";
import { HowItWorks } from "@/components/landing/HowItWorks";
import { Audience } from "@/components/landing/Audience";
import { AskPreview } from "@/components/landing/AskPreview";
import { Footer } from "@/components/landing/Footer";
import { FaqBubble } from "@/components/landing/FaqBubble";

export default function Home() {
  return (
    <>
      <Navbar />
      <main className="flex-1">
        <Hero />
        <Marquee />
        <Features />
        <HowItWorks />
        <Audience />
        <AskPreview />
      </main>
      <Footer />
      <FaqBubble />
    </>
  );
}

