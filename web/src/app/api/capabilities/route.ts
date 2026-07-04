import { NextResponse } from "next/server";
import { getWorkerUrl } from "@/lib/utils";

export async function GET() {
  try {
    const res = await fetch(`${getWorkerUrl()}/capabilities`, { cache: "no-store" });
    if (!res.ok) throw new Error("unavailable");
    return NextResponse.json(await res.json());
  } catch {
    return NextResponse.json(
      { ghostscript: false, qpdf: false, poppler: false, ocrmypdf: false },
      { status: 503 },
    );
  }
}
