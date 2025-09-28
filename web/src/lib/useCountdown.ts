import { useEffect, useState } from "react";

export function useCountdown(issuedAtISO?: string, etaMin?: number) {
  const [msLeft, setMsLeft] = useState<number>(() => {
    if (!issuedAtISO || !etaMin) return 0;
    const end = new Date(issuedAtISO).getTime() + etaMin * 60_000;
    return Math.max(0, end - Date.now());
  });

  useEffect(() => {
    if (!issuedAtISO || !etaMin) return;
    const end = new Date(issuedAtISO).getTime() + etaMin * 60_000;
    const id = setInterval(() => setMsLeft(Math.max(0, end - Date.now())), 1000);
    return () => clearInterval(id);
  }, [issuedAtISO, etaMin]);

  const total = Math.floor(msLeft / 1000);
  const h = Math.floor(total / 3600);
  const m = Math.floor((total % 3600) / 60);
  const s = total % 60;
  const formatted = `${String(h).padStart(2,"0")}:${String(m).padStart(2,"0")}:${String(s).padStart(2,"0")}`;
  return { msLeft, formatted };
}
