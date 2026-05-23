"use client";

import {
  createContext,
  useCallback,
  useContext,
  useEffect,
  useMemo,
  useState,
} from "react";
import {
  OnboardingState,
  emptyOnboardingState,
} from "./types";

const STORAGE_KEY = "lumi.onboarding";

type Updater = (prev: OnboardingState) => OnboardingState;

type OnboardingContextValue = {
  state: OnboardingState;
  update: (updater: Updater) => void;
  patch: <K extends keyof OnboardingState>(
    key: K,
    value: Partial<OnboardingState[K]> | OnboardingState[K]
  ) => void;
  reset: () => void;
  complete: () => void;
  isComplete: boolean;
  hydrated: boolean;
};

const OnboardingContext = createContext<OnboardingContextValue | null>(null);

export function OnboardingProvider({
  children,
}: {
  children: React.ReactNode;
}) {
  const [state, setState] = useState<OnboardingState>(emptyOnboardingState);
  const [hydrated, setHydrated] = useState(false);

  useEffect(() => {
    try {
      const raw = window.localStorage.getItem(STORAGE_KEY);
      if (raw) {
        const parsed = JSON.parse(raw) as Partial<OnboardingState>;
        setState({ ...emptyOnboardingState, ...parsed });
      }
    } catch {
      // ignore corrupt state
    }
    setHydrated(true);
  }, []);

  useEffect(() => {
    if (!hydrated) return;
    window.localStorage.setItem(STORAGE_KEY, JSON.stringify(state));
  }, [state, hydrated]);

  const update = useCallback((updater: Updater) => {
    setState((prev) => updater(prev));
  }, []);

  const patch = useCallback(
    <K extends keyof OnboardingState>(
      key: K,
      value: Partial<OnboardingState[K]> | OnboardingState[K]
    ) => {
      setState((prev) => {
        const current = prev[key];
        if (
          current &&
          typeof current === "object" &&
          !Array.isArray(current)
        ) {
          return {
            ...prev,
            [key]: { ...current, ...(value as object) },
          };
        }
        return { ...prev, [key]: value as OnboardingState[K] };
      });
    },
    []
  );

  const reset = useCallback(() => {
    setState(emptyOnboardingState);
    try {
      window.localStorage.removeItem(STORAGE_KEY);
    } catch {
      // ignore
    }
  }, []);

  const complete = useCallback(() => {
    setState((prev) => ({ ...prev, completedAt: new Date().toISOString() }));
  }, []);

  const value = useMemo<OnboardingContextValue>(
    () => ({
      state,
      update,
      patch,
      reset,
      complete,
      isComplete: Boolean(state.completedAt),
      hydrated,
    }),
    [state, update, patch, reset, complete, hydrated]
  );

  return (
    <OnboardingContext.Provider value={value}>
      {children}
    </OnboardingContext.Provider>
  );
}

export function useOnboarding() {
  const ctx = useContext(OnboardingContext);
  if (!ctx) {
    throw new Error("useOnboarding must be used within OnboardingProvider");
  }
  return ctx;
}
