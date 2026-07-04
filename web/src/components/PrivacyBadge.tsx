import { ShieldCheck } from "lucide-react";

export function PrivacyBadge() {
  return (
    <div className="flex items-center justify-center gap-2 text-sm text-vault-muted">
      <ShieldCheck className="w-4 h-4 text-emerald-400" />
      <span>
        Processed on your machine · deleted after download · no third-party uploads
      </span>
    </div>
  );
}
