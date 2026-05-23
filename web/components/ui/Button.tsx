"use client";

import { ButtonHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/cn";

type Variant = "primary" | "ghost" | "outline";

type Props = ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: Variant;
  fullWidth?: boolean;
};

const base =
  "inline-flex items-center justify-center rounded-2xl px-5 py-3 text-base font-medium transition-colors disabled:cursor-not-allowed disabled:opacity-50";

const variants: Record<Variant, string> = {
  primary:
    "bg-lumi-slate-400 text-white hover:bg-lumi-slate-600 active:bg-lumi-slate-600",
  outline:
    "border border-lumi-slate-200 bg-white text-lumi-slate-800 hover:border-lumi-slate-400 hover:text-lumi-slate-600",
  ghost: "text-lumi-slate-600 hover:bg-lumi-slate-100",
};

export const Button = forwardRef<HTMLButtonElement, Props>(function Button(
  { className, variant = "primary", fullWidth, type = "button", ...props },
  ref
) {
  return (
    <button
      ref={ref}
      type={type}
      className={cn(base, variants[variant], fullWidth && "w-full", className)}
      {...props}
    />
  );
});
