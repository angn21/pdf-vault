"use client";

import Link from "next/link";
import { WORKFLOW_PRESETS } from "@/lib/tools";

export default function WorkflowsPage() {
  return (
    <div className="max-w-3xl mx-auto px-4 py-12">
      <h1 className="text-3xl font-bold mb-2">Workflows</h1>
      <p className="text-vault-muted mb-8">
        Chain multiple PDF tools in one job. Pick a preset or build your own with the Workflow
        tool.
      </p>

      <div className="space-y-4">
        {WORKFLOW_PRESETS.map((preset) => (
          <div
            key={preset.id}
            className="rounded-xl border border-vault-border bg-vault-card p-6"
          >
            <h2 className="font-semibold mb-2">{preset.name}</h2>
            <ol className="text-sm text-vault-muted mb-4 list-decimal list-inside space-y-1">
              {preset.steps.map((step, i) => (
                <li key={i}>
                  {step.tool}
                  {Object.keys(step.options).length > 0 &&
                    ` (${JSON.stringify(step.options)})`}
                </li>
              ))}
            </ol>
            <Link
              href={`/tools/workflow`}
              className="text-sm text-vault-accent2 hover:underline"
            >
              Open Workflow tool →
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
      </div>
    </div>
  );
}
