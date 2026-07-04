import { NextRequest, NextResponse } from "next/server";
import { getWorkerUrl } from "@/lib/utils";

type Params = { params: Promise<{ jobId: string }> };

async function workerFetch(path: string, init?: RequestInit) {
  try {
    return await fetch(`${getWorkerUrl()}${path}`, init);
  } catch {
    return null;
  }
}

export async function GET(_request: NextRequest, { params }: Params) {
  const { jobId } = await params;
  const res = await workerFetch(`/jobs/${jobId}`, { cache: "no-store" });
  if (!res) {
    return NextResponse.json({ error: "PDF worker is not running" }, { status: 503 });
  }
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}

export async function DELETE(_request: NextRequest, { params }: Params) {
  const { jobId } = await params;
  const res = await workerFetch(`/jobs/${jobId}`, { method: "DELETE" });
  if (!res) {
    return NextResponse.json({ error: "PDF worker is not running" }, { status: 503 });
  }
  const data = await res.json();
  return NextResponse.json(data, { status: res.status });
}
