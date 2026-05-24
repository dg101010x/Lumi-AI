"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { Toggle } from "@/components/ui/Toggle";
import { StepLayout } from "@/components/onboarding/StepLayout";
import { useOnboarding } from "@/lib/onboarding-context";

export default function AlertsStep() {
  const router = useRouter();
  const { state, patch, complete } = useOnboarding();

  const [emergencySms, setEmergencySms] = useState(state.alerts.emergencySms);
  const [emergencyPush, setEmergencyPush] = useState(state.alerts.emergencyPush);
  const [medsReminders, setMedsReminders] = useState(state.alerts.medsReminders);
  const [quietHoursStart, setQuietHoursStart] = useState(
    state.alerts.quietHoursStart ?? ""
  );
  const [quietHoursEnd, setQuietHoursEnd] = useState(
    state.alerts.quietHoursEnd ?? ""
  );

  const handleNext = () => {
    patch("alerts", {
      emergencySms,
      emergencyPush,
      medsReminders,
      quietHoursStart: quietHoursStart || undefined,
      quietHoursEnd: quietHoursEnd || undefined,
    });
    complete();
    router.push("/");
  };

  return (
    <StepLayout
      step={6}
      total={6}
      title="How should we reach you?"
      subtitle="Emergencies always go out. Everything else is up to you."
      onNext={handleNext}
      nextLabel="Finish setup"
    >
      <div className="flex flex-col gap-3">
        <Toggle
          checked={emergencySms}
          onChange={setEmergencySms}
          label="Emergency SMS"
          description="Text every caregiver immediately on a fall or distress event"
        />
        <Toggle
          checked={emergencyPush}
          onChange={setEmergencyPush}
          label="Emergency push notifications"
          description="Same as above, but to the Lumi app"
        />
        <Toggle
          checked={medsReminders}
          onChange={setMedsReminders}
          label="Medication reminders"
          description="A gentle nudge if a scheduled dose is missed"
        />
      </div>

      <div className="mt-8">
        <p className="mb-3 text-sm font-medium text-lumi-slate-600">
          Quiet hours
        </p>
        <p className="mb-3 text-sm font-light text-lumi-slate-600">
          Non-emergency alerts are held until quiet hours end.
        </p>
        <div className="grid grid-cols-2 gap-3">
          <Field label="Start" htmlFor="quiet-start">
            <Input
              id="quiet-start"
              type="time"
              value={quietHoursStart}
              onChange={(e) => setQuietHoursStart(e.target.value)}
            />
          </Field>
          <Field label="End" htmlFor="quiet-end">
            <Input
              id="quiet-end"
              type="time"
              value={quietHoursEnd}
              onChange={(e) => setQuietHoursEnd(e.target.value)}
            />
          </Field>
        </div>
      </div>
    </StepLayout>
  );
}
