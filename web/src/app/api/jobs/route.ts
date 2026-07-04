import { NextRequest, NextResponse } from "next/server";
import { getWorkerUrl } from "@/lib/utils";

export async function POST(request: NextRequest) {
  const workerUrl = getWorkerUrl();
  const contentType = request.headers.get("content-type");

  if (!contentType?.includes("multipart/form-data")) {
    return NextResponse.json({ error: "Expected multipart form upload" }, { status: 400 });
  }

  try {
    const body = await request.arrayBuffer();
    const res = await fetch(`${workerUrl}/jobs`, {
      method: "POST",
      headers: { "content-type": contentType },
      body,
    });
    const data = await res.json();
    if (!res.ok) {
      return NextResponse.json({ error: data.detail || "Worker error" }, { status: res.status });
    }
    return NextResponse.json(data);
  } catch {
    return NextResponse.json(
      {
        error:
          "PDF worker is not running. Start it with: cd pdf-worker && uvicorn main:app --reload --port 8000",
        workerUrl,
      },
      { status: 503 },
    );
  }
}
