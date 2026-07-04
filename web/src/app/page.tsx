import { ToolCard } from "@/components/ToolCard";
import { CATEGORY_LABELS, TOOLS, type ToolCategory } from "@/lib/tools";

const ORDER: ToolCategory[] = [
  "organize",
  "optimize",
  "secure",
  "convert",
  "advanced",
  "automate",
];

export default function HomePage() {
  return (
    <div className="max-w-6xl mx-auto px-4 py-12">
      <section className="text-center mb-16">
        <h1 className="text-4xl md:text-5xl font-bold tracking-tight mb-4">
          Your PDF toolkit.
          <span className="block text-vault-accent2">Your machine.</span>
        </h1>
        <p className="text-vault-muted text-lg max-w-2xl mx-auto">
          Self-hosted alternative to cloud PDF services. Merge, split, compress, convert,
          and more — without sending files to strangers.
        </p>
      </section>

      {ORDER.map((category) => {
        const tools = TOOLS.filter((t) => t.category === category);
        if (!tools.length) return null;
        return (
          <section key={category} className="mb-12">
            <h2 className="text-xl font-semibold mb-4 text-vault-muted">
              {CATEGORY_LABELS[category]}
            </h2>
            <div className="grid sm:grid-cols-2 lg:grid-cols-3 gap-4">
              {tools.map((tool) => (
                <ToolCard key={tool.id} tool={tool} />
              ))}
            </div>
          </section>
        );
      })}
    </div>
  );
}
