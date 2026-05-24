"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { StepLayout } from "@/components/onboarding/StepLayout";
import { useOnboarding } from "@/lib/onboarding-context";

export default function WelcomeStep() {
  const router = useRouter();
  const { state, patch } = useOnboarding();

  const [name, setName] = useState(state.caregiver.name ?? "");
  const [email, setEmail] = useState(state.caregiver.email ?? "");
  const [phone, setPhone] = useState(state.caregiver.phone ?? "");

  const canProceed = name.trim().length > 0 && phone.trim().length > 0;

  const handleNext = () => {
    patch("caregiver", { name: name.trim(), email: email.trim(), phone: phone.trim() });
    router.push("/onboarding/resident");
  };

  return (
    <StepLayout
      step={1}
      total={6}
      title="Welcome to Lumi"
      subtitle="A care companion that never blinks. Let's set up your account."
      onNext={handleNext}
      nextLabel="Get started"
      canProceed={canProceed}
      showBack={false}
    >
      <div className="mb-8 flex justify-center">
        <div className="flex h-20 w-20 items-center justify-center rounded-full bg-lumi-slate-100">
          <span className="text-3xl font-medium text-lumi-slate-600">L</span>
        </div>
      </div>

      <Field label="Your name" htmlFor="caregiver-name">
        <Input
          id="caregiver-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Jamie Park"
          autoComplete="name"
        />
      </Field>

      <Field label="Email" htmlFor="caregiver-email" hint="Optional, used for account recovery">
        <Input
          id="caregiver-email"
          type="email"
          value={email}
          onChange={(e) => setEmail(e.target.value)}
          placeholder="you@example.com"
          autoComplete="email"
        />
      </Field>

      <Field label="Phone" htmlFor="caregiver-phone" hint="Used for emergency alerts">
        <Input
          id="caregiver-phone"
          type="tel"
          value={phone}
          onChange={(e) => setPhone(e.target.value)}
          placeholder="(555) 123-4567"
          autoComplete="tel"
        />
      </Field>
    </StepLayout>
  );
}
