import { cn } from "@/lib/cn";

type Props = {
  current: number;
  total: number;
};

export function ProgressDots({ current, total }: Props) {
  return (
    <div className="flex items-center gap-1.5" aria-label={`Step ${current} of ${total}`}>
      {Array.from({ length: total }).map((_, i) => {
        const idx = i + 1;
        const filled = idx <= current;
        return (
          <span
            key={i}
            className={cn(
              "h-1.5 rounded-full transition-all",
              filled ? "bg-lumi-slate-400" : "bg-lumi-slate-100",
              idx === current ? "w-6" : "w-1.5"
            )}
          />
        );
      })}
    </div>
  );
}
