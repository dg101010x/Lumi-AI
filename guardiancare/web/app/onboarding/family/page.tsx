"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Button } from "@/components/ui/Button";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { StepLayout } from "@/components/onboarding/StepLayout";
import { useOnboarding } from "@/lib/onboarding-context";
import type { FamilyMember } from "@/lib/types";

type Row = { name: string; phone: string; relationship: string };

const emptyRow = (): Row => ({ name: "", phone: "", relationship: "" });

export default function FamilyStep() {
  const router = useRouter();
  const { state, patch } = useOnboarding();

  const [rows, setRows] = useState<Row[]>(() => {
    if (state.family.length > 0) {
      return state.family.map((m) => ({
        name: m.name ?? "",
        phone: m.phone ?? "",
        relationship: m.relationship ?? "",
      }));
    }
    return [emptyRow()];
  });

  const updateRow = (index: number, key: keyof Row, value: string) => {
    setRows((prev) => prev.map((r, i) => (i === index ? { ...r, [key]: value } : r)));
  };

  const addRow = () => setRows((prev) => [...prev, emptyRow()]);
  const removeRow = (index: number) =>
    setRows((prev) => (prev.length === 1 ? prev : prev.filter((_, i) => i !== index)));

  const handleNext = () => {
    const cleaned: FamilyMember[] = rows
      .filter((r) => r.phone.trim().length > 0)
      .map((r) => ({
        name: r.name.trim() || undefined,
        phone: r.phone.trim(),
        relationship: r.relationship.trim() || undefined,
      }));
    patch("family", cleaned);
    router.push("/onboarding/alerts");
  };

  return (
    <StepLayout
      step={5}
      total={6}
      title="Add family caregivers"
      subtitle="They'll get a text the moment something needs attention. You can skip and add later."
      onNext={handleNext}
      nextLabel="Continue"
    >
      <div className="flex flex-col gap-4">
        {rows.map((row, i) => (
          <div
            key={i}
            className="rounded-2xl border border-lumi-slate-100 bg-white p-4"
          >
            <div className="mb-3 flex items-center justify-between">
              <span className="text-sm font-medium text-lumi-slate-600">
                Caregiver {i + 1}
              </span>
              {rows.length > 1 ? (
                <button
                  type="button"
                  onClick={() => removeRow(i)}
                  className="text-sm font-medium text-lumi-slate-600 hover:text-lumi-slate-800"
                >
                  Remove
                </button>
              ) : null}
            </div>

            <Field label="Name" htmlFor={`fam-name-${i}`}>
              <Input
                id={`fam-name-${i}`}
                value={row.name}
                onChange={(e) => updateRow(i, "name", e.target.value)}
                placeholder="Sarah Chen"
              />
            </Field>

            <Field label="Phone" htmlFor={`fam-phone-${i}`}>
              <Input
                id={`fam-phone-${i}`}
                type="tel"
                value={row.phone}
                onChange={(e) => updateRow(i, "phone", e.target.value)}
                placeholder="(555) 555-0123"
              />
            </Field>

            <Field label="Relationship" htmlFor={`fam-rel-${i}`}>
              <Input
                id={`fam-rel-${i}`}
                value={row.relationship}
                onChange={(e) => updateRow(i, "relationship", e.target.value)}
                placeholder="Daughter"
              />
            </Field>
          </div>
        ))}

        <Button variant="outline" onClick={addRow} fullWidth>
          + Add another caregiver
        </Button>
      </div>
    </StepLayout>
  );
}
