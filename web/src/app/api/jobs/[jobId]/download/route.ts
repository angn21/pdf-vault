import { NextRequest, NextResponse } from "next/server";
import { getWorkerUrl } from "@/lib/utils";

type Params = { params: Promise<{ jobId: string }> };

export async function GET(_request: NextRequest, { params }: Params) {
  const { jobId } = await params;
  const res = await fetch(`${getWorkerUrl()}/jobs/${jobId}/download`);
  if (!res.ok) {
    return NextResponse.json({ error: "Download not ready" }, { status: res.status });
  }
  const blob = await res.blob();
  const disposition = res.headers.get("content-disposition") || "";
  const filenameMatch = disposition.match(/filename="?([^"]+)"?/);
  const filename = filenameMatch?.[1] || "result.pdf";
  return new NextResponse(blob, {
    headers: {
      "Content-Type": res.headers.get("content-type") || "application/octet-stream",
      "Content-Disposition": `attachment; filename="${filename}"`,
    },
  });
}
