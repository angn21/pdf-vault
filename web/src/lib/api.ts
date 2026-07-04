export interface JobResponse {
  id: string;
  tool: string;
  status: "pending" | "processing" | "completed" | "failed";
  progress: number;
  message: string;
  error?: string | null;
  downloadUrl?: string | null;
  resultFilename?: string | null;
}

export async function createJob(
  tool: string,
  files: File[],
  options: Record<string, unknown>,
): Promise<{ jobId: string }> {
  const form = new FormData();
  form.append("tool", tool);
  form.append("options", JSON.stringify(options));
  files.forEach((file) => form.append("files", file));

  const res = await fetch("/api/jobs", { method: "POST", body: form });
  if (!res.ok) {
    const err = await res.json().catch(() => ({}));
    throw new Error(err.error || "Failed to create job");
  }
  return res.json();
}

export async function getJob(jobId: string): Promise<JobResponse> {
  const res = await fetch(`/api/jobs/${jobId}`);
  if (!res.ok) throw new Error("Job not found");
  return res.json();
}

export async function pollJob(
  jobId: string,
  onProgress?: (job: JobResponse) => void,
): Promise<JobResponse> {
  for (let i = 0; i < 120; i++) {
    const job = await getJob(jobId);
    onProgress?.(job);
    if (job.status === "completed" || job.status === "failed") return job;
    await new Promise((r) => setTimeout(r, 1000));
  }
  throw new Error("Job timed out");
}
