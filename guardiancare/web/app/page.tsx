"use client";

import { useEffect } from "react";
import { useRouter } from "next/navigation";
import { useOnboarding } from "@/lib/onboarding-context";

export default function HomePage() {
  const router = useRouter();
  const { isComplete, hydrated, state } = useOnboarding();

  useEffect(() => {
    if (!hydrated) return;
    if (!isComplete) {
      router.replace("/onboarding/welcome");
    }
  }, [hydrated, isComplete, router]);

  if (!hydrated || !isComplete) return null;

  const residentName =
    state.resident.nickname || state.resident.name || "your loved one";

  return (
    <main className="flex flex-1 flex-col items-center justify-center px-6 text-center">
      <div className="max-w-md">
        <div className="mb-6 inline-flex h-16 w-16 items-center justify-center rounded-full bg-lumi-slate-100">
          <span className="text-2xl text-lumi-slate-600 font-medium">L</span>
        </div>
        <h1 className="mb-2 text-2xl font-medium text-lumi-slate-800">
          You&apos;re all set
        </h1>
        <p className="font-light text-lumi-slate-600">
          Lumi is watching over {residentName}. The home dashboard will live
          here once it&apos;s built.
        </p>
      </div>
    </main>
  );
}
