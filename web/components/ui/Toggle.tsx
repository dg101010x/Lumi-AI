"use client";

import { cn } from "@/lib/cn";

type Props = {
  checked: boolean;
  onChange: (next: boolean) => void;
  label: string;
  description?: string;
};

export function Toggle({ checked, onChange, label, description }: Props) {
  return (
    <label className="flex cursor-pointer items-start justify-between gap-4 rounded-2xl border border-lumi-slate-100 bg-white p-4">
      <span className="flex-1">
        <span className="block text-base font-medium text-lumi-slate-800">
          {label}
        </span>
        {description ? (
          <span className="mt-1 block text-sm font-light text-lumi-slate-600">
            {description}
          </span>
        ) : null}
      </span>
      <span className="relative inline-block h-6 w-11 shrink-0">
        <input
          type="checkbox"
          className="peer absolute inset-0 z-10 cursor-pointer opacity-0"
          checked={checked}
          onChange={(e) => onChange(e.target.checked)}
        />
        <span
          className={cn(
            "block h-6 w-11 rounded-full transition-colors",
            checked ? "bg-lumi-slate-400" : "bg-lumi-slate-100"
          )}
        />
        <span
          className={cn(
            "absolute top-0.5 left-0.5 block h-5 w-5 rounded-full bg-white shadow-sm transition-transform",
            checked && "translate-x-5"
          )}
        />
      </span>
    </label>
  );
}
