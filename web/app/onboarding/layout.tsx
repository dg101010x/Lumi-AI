export default function OnboardingLayout({
  children,
}: {
  children: React.ReactNode;
}) {
  return (
    <div className="flex min-h-dvh w-full justify-center bg-lumi-slate-50">
      <div className="flex w-full max-w-md flex-col">{children}</div>
    </div>
  );
}
