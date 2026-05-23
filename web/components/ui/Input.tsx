"use client";

import { InputHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/cn";

type Props = InputHTMLAttributes<HTMLInputElement>;

export const Input = forwardRef<HTMLInputElement, Props>(function Input(
  { className, ...props },
  ref
) {
  return (
    <input
      ref={ref}
      className={cn(
        "w-full rounded-2xl border border-lumi-slate-100 bg-white px-4 py-3 text-base text-lumi-slate-800 placeholder:text-lumi-slate-200 focus:border-lumi-slate-400 focus:outline-none focus:ring-2 focus:ring-lumi-slate-100",
        className
      )}
      {...props}
    />
  );
});
