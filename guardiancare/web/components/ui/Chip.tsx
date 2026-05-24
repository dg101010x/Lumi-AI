"use client";

import { ButtonHTMLAttributes } from "react";
import { cn } from "@/lib/cn";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  selected?: boolean;
};

export function Chip({ selected, className, type = "button", ...props }: Props) {
  return (
    <button
      type={type}
      className={cn(
        "rounded-full border px-4 py-2 text-sm font-normal transition-colors",
        selected
          ? "border-lumi-slate-400 bg-lumi-slate-400 text-white"
          : "border-lumi-slate-100 bg-white text-lumi-slate-600 hover:border-lumi-slate-200",
        className
      )}
      {...props}
    />
  );
}
