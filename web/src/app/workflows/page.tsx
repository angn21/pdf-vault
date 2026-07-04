"use client";

import Link from "next/link";
import { WORKFLOW_PRESETS } from "@/lib/tools";

export default function WorkflowsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-2">Workflows</h1>
      <p className="text-vault-muted mb-8">
        Chain multiple PDF tools in one job. Pick a preset to load it in the Workflow tool, or
        build your own from scratch.
      </p>

      <div className="grid gap-4 sm:grid-cols-2">
        {WORKFLOW_PRESETS.map((preset) => (
          <div
            key={preset.id}
            className="rounded-xl border border-vault-border bg-vault-card p-5 flex flex-col"
          >
            <h2 className="font-semibold mb-1">{preset.name}</h2>
            <p className="text-sm text-vault-muted mb-3 flex-1">{preset.description}</p>
            <ol className="text-xs text-vault-muted mb-4 list-decimal list-inside space-y-0.5">
              {preset.steps.map((step, i) => (
                <li key={i}>{step.tool}</li>
              ))}
            </ol>
            <Link
              href={`/tools/workflow?preset=${preset.id}`}
              className="text-sm text-vault-accent2 hover:underline"
            >
              Use this workflow →
            </Link>
          </div>
        ))}
      </div>

      <div className="mt-8 rounded-xl border border-dashed border-vault-border p-6 text-sm text-vault-muted">
        <p className="mb-2 font-medium text-white">Custom workflow JSON example:</p>
        <pre className="bg-vault-bg rounded-lg p-4 overflow-x-auto text-xs">
{`[
  {"tool": "compress", "options": {"quality": "ebook"}},
  {"tool": "watermark", "options": {"text": "DRAFT"}},
  {"tool": "protect", "options": {"password": "secret"}}
]`}
        </pre>
        <Link href="/tools/workflow" className="inline-block mt-4 text-vault-accent2 hover:underline">
          Open blank Workflow tool →
        </Link>
      </div>
    </div>
  );
}
