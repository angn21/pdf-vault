import { Suspense } from "react";
import { notFound } from "next/navigation";
import { ToolWizard } from "@/components/ToolWizard";
import { getTool } from "@/lib/tools";

type Props = { params: Promise<{ toolId: string }> };

export default async function ToolPage({ params }: Props) {
  const { toolId } = await params;
  const tool = getTool(toolId);
  if (!tool) notFound();

  return (
    <div className="max-w-2xl mx-auto px-4 py-12">
      <div className="mb-8">
        <a href="/" className="text-sm text-vault-muted hover:text-white">
          ← All tools
        </a>
        <h1 className="text-3xl font-bold mt-4 mb-2">{tool.name}</h1>
        <p className="text-vault-muted">{tool.description}</p>
      </div>
      <Suspense fallback={<div className="text-vault-muted text-sm">Loading…</div>}>
        <ToolWizard tool={tool} />
      </Suspense>
    </div>
  );
}
