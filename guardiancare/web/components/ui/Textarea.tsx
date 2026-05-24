"use client";

import { TextareaHTMLAttributes, forwardRef } from "react";
import { cn } from "@/lib/cn";

type Props = TextareaHTMLAttributes<HTMLTextAreaElement>;

export const Textarea = forwardRef<HTMLTextAreaElement, Props>(
  function Textarea({ className, rows = 3, ...props }, ref) {
    return (
      <textarea
        ref={ref}
        rows={rows}
        className={cn(
          "w-full resize-none rounded-2xl border border-lumi-slate-100 bg-white px-4 py-3 text-base text-lumi-slate-800 placeholder:text-lumi-slate-200 focus:border-lumi-slate-400 focus:outline-none focus:ring-2 focus:ring-lumi-slate-100",
          className
        )}
        {...props}
      />
    );
  }
);
