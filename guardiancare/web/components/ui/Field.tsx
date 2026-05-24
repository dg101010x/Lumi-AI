"use client";

import { ReactNode } from "react";
import { Label } from "./Label";

type Props = {
  label: string;
  htmlFor?: string;
  hint?: string;
  children: ReactNode;
};

export function Field({ label, htmlFor, hint, children }: Props) {
  return (
    <div className="mb-4">
      <Label htmlFor={htmlFor}>{label}</Label>
      {children}
      {hint ? (
        <p className="mt-1 text-xs font-light text-lumi-slate-600">{hint}</p>
      ) : null}
    </div>
  );
}
