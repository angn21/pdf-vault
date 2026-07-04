import Link from "next/link";
import type { ToolDefinition } from "@/lib/tools";
import { cn } from "@/lib/utils";

const categoryColors: Record<string, string> = {
  organize: "from-blue-500/20 to-blue-600/5 border-blue-500/30",
  optimize: "from-emerald-500/20 to-emerald-600/5 border-emerald-500/30",
  secure: "from-amber-500/20 to-amber-600/5 border-amber-500/30",
  convert: "from-purple-500/20 to-purple-600/5 border-purple-500/30",
  advanced: "from-rose-500/20 to-rose-600/5 border-rose-500/30",
  automate: "from-cyan-500/20 to-cyan-600/5 border-cyan-500/30",
};

export function ToolCard({ tool }: { tool: ToolDefinition }) {
  return (
    <Link
      href={`/tools/${tool.id}`}
      className={cn(
        "group block rounded-xl border bg-gradient-to-br p-5 transition-all hover:scale-[1.02] hover:drop-glow",
        categoryColors[tool.category] || "from-vault-card to-vault-bg border-vault-border",
      )}
    >
      <h3 className="font-semibold mb-1 group-hover:text-vault-accent2 transition-colors">
        {tool.name}
      </h3>
      <p className="text-sm text-vault-muted leading-relaxed">{tool.description}</p>
    </Link>
  );
}
