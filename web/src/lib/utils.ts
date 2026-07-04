import { clsx, type ClassValue } from "clsx";
import { twMerge } from "tailwind-merge";

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function getWorkerUrl(): string {
  return process.env.PDF_WORKER_URL || "http://localhost:8000";
}

/** Parse page numbers from comma-separated input; supports ranges like 2-4. */
export function parsePageNumbers(input: string): number[] {
  const pages = new Set<number>();
  for (const part of input.split(",")) {
    const token = part.trim();
    if (!token) continue;
    if (token.includes("-")) {
      const [startS, endS] = token.split("-", 2);
      let start = parseInt(startS.trim(), 10);
      let end = parseInt(endS.trim(), 10);
      if (start > end) [start, end] = [end, start];
      for (let p = start; p <= end; p++) pages.add(p);
    } else {
      pages.add(parseInt(token, 10));
    }
  }
  return [...pages].sort((a, b) => a - b);
}
