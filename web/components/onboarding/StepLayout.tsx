"use client";

import { ReactNode } from "react";
import { useRouter } from "next/navigation";
import { Button } from "@/components/ui/Button";
import { ProgressDots } from "./ProgressDots";

type Props = {
  step: number;
  total: number;
  title: string;
  subtitle?: string;
  children: ReactNode;
  onNext: () => void;
  nextLabel?: string;
  canProceed?: boolean;
  showBack?: boolean;
};

export function StepLayout({
  step,
  total,
  title,
  subtitle,
  children,
  onNext,
  nextLabel = "Continue",
  canProceed = true,
  showBack = true,
}: Props) {
  const router = useRouter();

  return (
    <div className="flex min-h-dvh flex-col">
      <header className="flex items-center justify-between px-6 pt-6">
        {showBack ? (
          <button
            type="button"
            onClick={() => router.back()}
            className="text-sm font-medium text-lumi-slate-600 hover:text-lumi-slate-800"
            aria-label="Go back"
          >
            ← Back
          </button>
        ) : (
          <span className="h-5 w-12" />
        )}
        <ProgressDots current={step} total={total} />
        <span className="h-5 w-12" />
      </header>

      <main className="flex flex-1 flex-col px-6 pt-8 pb-6">
        <h1 className="text-2xl font-medium text-lumi-slate-800">{title}</h1>
        {subtitle ? (
          <p className="mt-2 font-light text-lumi-slate-600">{subtitle}</p>
        ) : null}
        <div className="mt-8 flex-1">{children}</div>
      </main>

      <footer className="border-t border-lumi-slate-100 bg-white px-6 py-4">
        <Button onClick={onNext} disabled={!canProceed} fullWidth>
          {nextLabel}
        </Button>
      </footer>
    </div>
  );
}
