"use client";

import { useCallback, useEffect, useState } from "react";
import { useSearchParams } from "next/navigation";
import { Download, Loader2, Upload } from "lucide-react";
import type { ToolDefinition } from "@/lib/tools";
import { getWorkflowPreset } from "@/lib/tools";
import { createJob, pollJob, type JobResponse } from "@/lib/api";
import { cn, parsePageNumbers } from "@/lib/utils";

interface ToolWizardProps {
  tool: ToolDefinition;
}

export function ToolWizard({ tool }: ToolWizardProps) {
  const searchParams = useSearchParams();
  const [files, setFiles] = useState<File[]>([]);
  const [options, setOptions] = useState<Record<string, string>>(() => {
    const defaults: Record<string, string> = {};
    tool.options?.forEach((opt) => {
      if (opt.default !== undefined) defaults[opt.key] = String(opt.default);
    });
    return defaults;
  });
  const [dragging, setDragging] = useState(false);
  const [job, setJob] = useState<JobResponse | null>(null);
  const [error, setError] = useState<string | null>(null);
  const [processing, setProcessing] = useState(false);

  useEffect(() => {
    if (tool.id !== "workflow") return;
    const presetId = searchParams.get("preset");
    if (!presetId) return;
    const preset = getWorkflowPreset(presetId);
    if (!preset) return;
    setOptions((prev) => ({
      ...prev,
      steps: JSON.stringify(preset.steps, null, 2),
    }));
  }, [tool.id, searchParams]);

  const accept = tool.accept;

  const onFiles = useCallback(
    (incoming: FileList | null) => {
      if (!incoming?.length) return;
      const list = Array.from(incoming).filter((f) => f?.name);
      if (!list.length) return;
      setFiles(tool.multiple ? list : [list[0]]);
    },
    [tool.multiple],
  );

  const buildOptions = (): Record<string, unknown> => {
    const parsed: Record<string, unknown> = { ...options };
    if (tool.id === "organize" && options.pageOrder) {
      parsed.pageOrder = options.pageOrder.split(",").map((s) => parseInt(s.trim(), 10));
    }
    if (tool.id === "remove-pages" && options.removePages) {
      parsed.removePages = parsePageNumbers(options.removePages);
    }
    if (tool.id === "workflow" && options.steps) {
      try {
        parsed.steps = JSON.parse(options.steps);
      } catch {
        throw new Error("Invalid workflow steps JSON");
      }
    }
    if (tool.id === "redact" && options.boxes) {
      try {
        parsed.boxes = JSON.parse(options.boxes);
      } catch {
        throw new Error("Invalid redaction boxes JSON");
      }
    }
    if (tool.multiple && files.length) {
      parsed.fileOrder = files.filter((f) => f?.name).map((f) => f.name);
    }
    return parsed;
  };

  const handleProcess = async () => {
    if (!files.length) {
      setError("Please upload at least one file.");
      return;
    }
    setError(null);
    setProcessing(true);
    setJob(null);
    try {
      const { jobId } = await createJob(tool.id, files, buildOptions());
      const result = await pollJob(jobId, setJob);
      if (result.status === "failed") {
        setError(result.error || "Processing failed");
      } else {
        setJob(result);
      }
    } catch (e) {
      setError(e instanceof Error ? e.message : "Something went wrong");
    } finally {
      setProcessing(false);
    }
  };

  return (
    <div className="space-y-6">
      <div
        onDragOver={(e) => {
          e.preventDefault();
          setDragging(true);
        }}
        onDragLeave={() => setDragging(false)}
        onDrop={(e) => {
          e.preventDefault();
          setDragging(false);
          onFiles(e.dataTransfer.files);
        }}
        className={cn(
          "relative rounded-2xl border-2 border-dashed p-12 text-center transition-all",
          dragging
            ? "border-vault-accent bg-vault-accent/10 drop-glow"
            : "border-vault-border bg-vault-card/50 hover:border-vault-accent/50",
        )}
      >
        <Upload className="w-10 h-10 mx-auto mb-4 text-vault-muted" />
        <p className="text-lg font-medium mb-2">Drop files here</p>
        <p className="text-sm text-vault-muted mb-4">or click to browse · {accept}</p>
        <input
          type="file"
          accept={accept}
          multiple={tool.multiple}
          className="absolute inset-0 opacity-0 cursor-pointer"
          onChange={(e) => onFiles(e.target.files)}
        />
        {files.length > 0 && (
          <div className="mt-4 text-sm text-vault-accent2">
            {files.map((f) => f?.name).filter(Boolean).join(", ")}
          </div>
        )}
      </div>

      {tool.options && tool.options.length > 0 && (
        <div className="rounded-xl border border-vault-border bg-vault-card p-6 space-y-4">
          <h3 className="font-medium">Options</h3>
          {tool.options.map((opt) => (
            <label key={opt.key} className="block space-y-1">
              <span className="text-sm text-vault-muted">{opt.label}</span>
              {opt.type === "select" ? (
                <select
                  className="w-full rounded-lg bg-vault-bg border border-vault-border px-3 py-2"
                  value={options[opt.key] || ""}
                  onChange={(e) => setOptions({ ...options, [opt.key]: e.target.value })}
                >
                  {opt.choices?.map((c) => (
                    <option key={c.value} value={c.value}>
                      {c.label}
                    </option>
                  ))}
                </select>
              ) : opt.type === "textarea" ? (
                <textarea
                  className="w-full rounded-lg bg-vault-bg border border-vault-border px-3 py-2 min-h-[100px] font-mono text-sm"
                  placeholder={opt.placeholder}
                  value={options[opt.key] || ""}
                  onChange={(e) => setOptions({ ...options, [opt.key]: e.target.value })}
                />
              ) : (
                <input
                  type={opt.type === "number" ? "number" : "text"}
                  className="w-full rounded-lg bg-vault-bg border border-vault-border px-3 py-2"
                  placeholder={opt.placeholder}
                  value={options[opt.key] || ""}
                  onChange={(e) => setOptions({ ...options, [opt.key]: e.target.value })}
                />
              )}
            </label>
          ))}
        </div>
      )}

      <button
        onClick={handleProcess}
        disabled={processing || !files.length}
        className="w-full rounded-xl bg-gradient-to-r from-vault-accent to-vault-accent2 py-3 font-semibold disabled:opacity-50 flex items-center justify-center gap-2"
      >
        {processing ? (
          <>
            <Loader2 className="w-5 h-5 animate-spin" />
            {job?.message || "Processing…"}
          </>
        ) : (
          `Process with ${tool.name}`
        )}
      </button>

      {processing && job && (
        <div className="rounded-xl border border-vault-border bg-vault-card p-4">
          <div className="flex justify-between text-sm mb-2">
            <span>{job.status}</span>
            <span>{Math.round(job.progress)}%</span>
          </div>
          <div className="h-2 rounded-full bg-vault-bg overflow-hidden">
            <div
              className="h-full bg-vault-accent transition-all animate-pulseRing"
              style={{ width: `${Math.max(job.progress, 15)}%` }}
            />
          </div>
        </div>
      )}

      {error && (
        <div className="rounded-xl border border-red-500/50 bg-red-500/10 p-4 text-red-300 text-sm">
          {error}
        </div>
      )}

      {job?.status === "completed" && job.id && (
        <a
          href={`/api/jobs/${job.id}/download`}
          className="flex items-center justify-center gap-2 w-full rounded-xl border border-emerald-500/50 bg-emerald-500/10 py-3 text-emerald-300 font-medium hover:bg-emerald-500/20 transition-colors"
        >
          <Download className="w-5 h-5" />
          Download {job.resultFilename || "result"}
        </a>
      )}
    </div>
  );
}
