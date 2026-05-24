"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { StepLayout } from "@/components/onboarding/StepLayout";
import { useOnboarding } from "@/lib/onboarding-context";

export default function ResidentStep() {
  const router = useRouter();
  const { state, patch } = useOnboarding();

  const [name, setName] = useState(state.resident.name ?? "");
  const [nickname, setNickname] = useState(state.resident.nickname ?? "");
  const [dob, setDob] = useState(state.resident.dob ?? "");
  const [room, setRoom] = useState(state.resident.room ?? "");

  const canProceed = name.trim().length > 0;

  const handleNext = () => {
    patch("resident", {
      name: name.trim(),
      nickname: nickname.trim(),
      dob,
      room: room.trim(),
    });
    router.push("/onboarding/health");
  };

  return (
    <StepLayout
      step={2}
      total={6}
      title="Who is Lumi watching over?"
      subtitle="Tell us a little about your loved one."
      onNext={handleNext}
      canProceed={canProceed}
    >
      <Field label="Full name" htmlFor="resident-name">
        <Input
          id="resident-name"
          value={name}
          onChange={(e) => setName(e.target.value)}
          placeholder="Margaret Chen"
        />
      </Field>

      <Field label="What do they like to be called?" htmlFor="resident-nickname" hint="Lumi uses this in conversation">
        <Input
          id="resident-nickname"
          value={nickname}
          onChange={(e) => setNickname(e.target.value)}
          placeholder="Maggie"
        />
      </Field>

      <Field label="Date of birth" htmlFor="resident-dob">
        <Input
          id="resident-dob"
          type="date"
          value={dob}
          onChange={(e) => setDob(e.target.value)}
        />
      </Field>

      <Field label="Room or location" htmlFor="resident-room" hint="Where the Lumi device is placed">
        <Input
          id="resident-room"
          value={room}
          onChange={(e) => setRoom(e.target.value)}
          placeholder="Living room"
        />
      </Field>
    </StepLayout>
  );
}
