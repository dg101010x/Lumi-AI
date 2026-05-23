"use client";

import { useRouter } from "next/navigation";
import { useState } from "react";
import { Field } from "@/components/ui/Field";
import { Input } from "@/components/ui/Input";
import { Textarea } from "@/components/ui/Textarea";
import { StepLayout } from "@/components/onboarding/StepLayout";
import { useOnboarding } from "@/lib/onboarding-context";

export default function LikesStep() {
  const router = useRouter();
  const { state, patch } = useOnboarding();

  const [music, setMusic] = useState(state.likes.music ?? "");
  const [food, setFood] = useState(state.likes.food ?? "");
  const [hobbies, setHobbies] = useState(state.likes.hobbies ?? "");
  const [family, setFamily] = useState(state.likes.family ?? "");

  const handleNext = () => {
    patch("likes", {
      music: music.trim(),
      food: food.trim(),
      hobbies: hobbies.trim(),
      family: family.trim(),
    });
    router.push("/onboarding/family");
  };

  return (
    <StepLayout
      step={4}
      total={6}
      title="What do they love?"
      subtitle="Lumi uses these in everyday conversations to feel familiar."
      onNext={handleNext}
    >
      <Field label="Favorite music or artists" htmlFor="music">
        <Input
          id="music"
          value={music}
          onChange={(e) => setMusic(e.target.value)}
          placeholder="Frank Sinatra, classical piano"
        />
      </Field>

      <Field label="Favorite foods" htmlFor="food">
        <Input
          id="food"
          value={food}
          onChange={(e) => setFood(e.target.value)}
          placeholder="Chicken soup, pumpkin pie"
        />
      </Field>

      <Field label="Hobbies and interests" htmlFor="hobbies">
        <Input
          id="hobbies"
          value={hobbies}
          onChange={(e) => setHobbies(e.target.value)}
          placeholder="Knitting, watching baseball, crosswords"
        />
      </Field>

      <Field label="Family Lumi should know about" htmlFor="family" hint="Names of people they talk about often">
        <Textarea
          id="family"
          value={family}
          onChange={(e) => setFamily(e.target.value)}
          placeholder="Husband Tom (passed 2019), daughter Sarah, grandkids Mia and Eli"
          rows={3}
        />
      </Field>
    </StepLayout>
  );
}
