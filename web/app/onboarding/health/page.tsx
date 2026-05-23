"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Chip } from "@/components/ui/Chip";
import { Field } from "@/components/ui/Field";
import { StepLayout } from "@/components/onboarding/StepLayout";
import { useOnboarding } from "@/lib/onboarding-context";
import type { Mobility } from "@/lib/types";

const COMMON_CONDITIONS = [
  "Dementia",
  "Alzheimer's",
  "Parkinson's",
  "Diabetes",
  "Heart condition",
  "High blood pressure",
  "Arthritis",
  "Stroke history",
  "Vision impairment",
  "Hearing impairment",
];

const MOBILITY_OPTIONS: { value: Mobility; label: string; description: string }[] = [
  { value: "independent", label: "Independent", description: "Walks without aid" },
  { value: "walker", label: "Uses a walker or cane", description: "Walks with support" },
  { value: "wheelchair", label: "Uses a wheelchair", description: "Mostly seated" },
  { value: "bed", label: "Mostly bed-bound", description: "Limited movement" },
];

export default function HealthStep() {
  const router = useRouter();
  const { state, patch } = useOnboarding();

  const [conditions, setConditions] = useState<string[]>(state.health.conditions);
  const [mobility, setMobility] = useState<Mobility | undefined>(state.health.mobility);

  const canProceed = Boolean(mobility);

  const toggleCondition = (c: string) => {
    setConditions((prev) =>
      prev.includes(c) ? prev.filter((x) => x !== c) : [...prev, c]
    );
  };

  const handleNext = () => {
    patch("health", { conditions, mobility });
    router.push("/onboarding/likes");
  };

  return (
    <StepLayout
      step={3}
      total={6}
      title="Health and mobility"
      subtitle="Helps Lumi know what to watch for and how to respond."
      onNext={handleNext}
      canProceed={canProceed}
    >
      <Field label="Any conditions? Select all that apply.">
        <div className="flex flex-wrap gap-2">
          {COMMON_CONDITIONS.map((c) => (
            <Chip
              key={c}
              selected={conditions.includes(c)}
              onClick={() => toggleCondition(c)}
            >
              {c}
            </Chip>
          ))}
        </div>
      </Field>

      <Field label="Mobility">
        <div className="flex flex-col gap-2">
          {MOBILITY_OPTIONS.map((opt) => {
            const selected = mobility === opt.value;
            return (
              <button
                key={opt.value}
                type="button"
                onClick={() => setMobility(opt.value)}
                className={
                  "rounded-2xl border bg-white p-4 text-left transition-colors " +
                  (selected
                    ? "border-lumi-slate-400 ring-2 ring-lumi-slate-100"
                    : "border-lumi-slate-100 hover:border-lumi-slate-200")
                }
              >
                <span className="block text-base font-medium text-lumi-slate-800">
                  {opt.label}
                </span>
                <span className="mt-1 block text-sm font-light text-lumi-slate-600">
                  {opt.description}
                </span>
              </button>
            );
          })}
        </div>
      </Field>
    </StepLayout>
  );
}
