export type ToolCategory = "organize" | "optimize" | "secure" | "convert" | "advanced" | "automate";

export interface ToolDefinition {
  id: string;
  name: string;
  description: string;
  category: ToolCategory;
  accept: string;
  multiple?: boolean;
  options?: ToolOption[];
}

export interface ToolOption {
  key: string;
  label: string;
  type: "text" | "number" | "select" | "textarea" | "pages";
  default?: string | number;
  choices?: { label: string; value: string }[];
  placeholder?: string;
}

export const CATEGORY_LABELS: Record<ToolCategory, string> = {
  organize: "Organize",
  optimize: "Optimize",
  secure: "Secure",
  convert: "Convert",
  advanced: "Advanced",
  automate: "Automate",
};

export const TOOLS: ToolDefinition[] = [
  {
    id: "merge",
    name: "Merge PDF",
    description: "Combine multiple PDFs into one document.",
    category: "organize",
    accept: ".pdf",
    multiple: true,
  },
  {
    id: "split",
    name: "Split PDF",
    description: "Extract pages or split into multiple files.",
    category: "organize",
    accept: ".pdf",
    options: [
      {
        key: "mode",
        label: "Split mode",
        type: "select",
        default: "ranges",
        choices: [
          { label: "Page ranges", value: "ranges" },
          { label: "Every N pages", value: "every_n" },
        ],
      },
      { key: "ranges", label: "Page ranges (e.g. 1-3,5)", type: "text", default: "1" },
      { key: "everyN", label: "Pages per file", type: "number", default: 1 },
    ],
  },
  {
    id: "compress",
    name: "Compress PDF",
    description: "Reduce file size for sharing and storage.",
    category: "optimize",
    accept: ".pdf",
    options: [
      {
        key: "quality",
        label: "Quality",
        type: "select",
        default: "ebook",
        choices: [
          { label: "Screen (smallest)", value: "screen" },
          { label: "eBook", value: "ebook" },
          { label: "Printer", value: "printer" },
          { label: "Prepress (largest)", value: "prepress" },
        ],
      },
    ],
  },
  {
    id: "rotate",
    name: "Rotate PDF",
    description: "Rotate all pages by 90, 180, or 270 degrees.",
    category: "organize",
    accept: ".pdf",
    options: [
      {
        key: "angle",
        label: "Rotation",
        type: "select",
        default: "90",
        choices: [
          { label: "90°", value: "90" },
          { label: "180°", value: "180" },
          { label: "270°", value: "270" },
        ],
      },
    ],
  },
  {
    id: "organize",
    name: "Organize PDF",
    description: "Reorder pages by specifying a new page order.",
    category: "organize",
    accept: ".pdf",
    options: [
      {
        key: "pageOrder",
        label: "Page order (comma-separated, e.g. 3,1,2)",
        type: "text",
        placeholder: "1,2,3",
      },
    ],
  },
  {
    id: "remove-pages",
    name: "Remove Pages",
    description: "Delete specific pages from a PDF.",
    category: "organize",
    accept: ".pdf",
    options: [
      {
        key: "removePages",
        label: "Pages to remove (comma-separated, ranges like 2-4)",
        type: "text",
        placeholder: "2,4 or 2-4",
      },
    ],
  },
  {
    id: "protect",
    name: "Protect PDF",
    description: "Add a password to open the PDF.",
    category: "secure",
    accept: ".pdf",
    options: [{ key: "password", label: "Password", type: "text" }],
  },
  {
    id: "unlock",
    name: "Unlock PDF",
    description: "Remove password protection from a PDF.",
    category: "secure",
    accept: ".pdf",
    options: [{ key: "password", label: "Current password", type: "text" }],
  },
  {
    id: "watermark",
    name: "Watermark",
    description: "Add a text watermark across all pages.",
    category: "secure",
    accept: ".pdf",
    options: [{ key: "text", label: "Watermark text", type: "text", default: "CONFIDENTIAL" }],
  },
  {
    id: "page-numbers",
    name: "Page Numbers",
    description: "Add page numbers to your document.",
    category: "organize",
    accept: ".pdf",
    options: [
      {
        key: "position",
        label: "Position",
        type: "select",
        default: "bottom-center",
        choices: [
          { label: "Bottom center", value: "bottom-center" },
          { label: "Bottom right", value: "bottom-right" },
          { label: "Bottom left", value: "bottom-left" },
        ],
      },
    ],
  },
  {
    id: "pdf-to-jpg",
    name: "PDF to JPG",
    description: "Convert each PDF page to JPG images.",
    category: "convert",
    accept: ".pdf",
    options: [
      {
        key: "format",
        label: "Format",
        type: "select",
        default: "jpeg",
        choices: [
          { label: "JPEG", value: "jpeg" },
          { label: "PNG", value: "png" },
        ],
      },
    ],
  },
  {
    id: "images-to-pdf",
    name: "Images to PDF",
    description: "Combine JPG or PNG images into a PDF.",
    category: "convert",
    accept: ".jpg,.jpeg,.png",
    multiple: true,
  },
  {
    id: "extract-images",
    name: "Extract Images",
    description: "Pull embedded images out of a PDF.",
    category: "convert",
    accept: ".pdf",
  },
  {
    id: "pdf-to-word",
    name: "PDF to Word",
    description: "Convert PDF to an editable DOCX file.",
    category: "convert",
    accept: ".pdf",
  },
  {
    id: "ocr",
    name: "OCR PDF",
    description: "Make scanned PDFs searchable with OCR.",
    category: "advanced",
    accept: ".pdf",
  },
  {
    id: "repair",
    name: "Repair PDF",
    description: "Attempt to fix a corrupted PDF file.",
    category: "advanced",
    accept: ".pdf",
  },
  {
    id: "pdf-to-pdfa",
    name: "PDF to PDF/A",
    description: "Convert to archival PDF/A format.",
    category: "advanced",
    accept: ".pdf",
  },
  {
    id: "compare",
    name: "Compare PDF",
    description: "Compare two PDF files and generate a report.",
    category: "advanced",
    accept: ".pdf",
    multiple: true,
  },
  {
    id: "redact",
    name: "Redact PDF",
    description: "Redact regions (provide boxes JSON in options).",
    category: "advanced",
    accept: ".pdf",
    options: [
      {
        key: "boxes",
        label: "Redaction boxes JSON",
        type: "textarea",
        placeholder: '[{"page":1,"x":50,"y":50,"width":200,"height":30}]',
      },
    ],
  },
  {
    id: "crop",
    name: "Crop PDF",
    description: "Crop margins from all pages.",
    category: "organize",
    accept: ".pdf",
    options: [{ key: "margin", label: "Margin to remove (pt)", type: "number", default: 20 }],
  },
  {
    id: "sign",
    name: "Sign PDF",
    description: "Overlay a signature image on the first page.",
    category: "secure",
    accept: ".pdf,.png,.jpg,.jpeg",
    multiple: true,
    options: [
      { key: "signatureFile", label: "Signature filename (from uploads)", type: "text" },
      { key: "x", label: "X position", type: "number", default: 50 },
      { key: "y", label: "Y position", type: "number", default: 50 },
      { key: "width", label: "Width", type: "number", default: 150 },
    ],
  },
  {
    id: "workflow",
    name: "Workflow",
    description: "Chain multiple tools in one job.",
    category: "automate",
    accept: ".pdf",
    multiple: true,
    options: [
      {
        key: "steps",
        label: "Steps JSON",
        type: "textarea",
        placeholder:
          '[{"tool":"compress","options":{"quality":"ebook"}},{"tool":"watermark","options":{"text":"DRAFT"}}]',
      },
    ],
  },
];

export function getTool(id: string): ToolDefinition | undefined {
  return TOOLS.find((t) => t.id === id);
}

export interface WorkflowStep {
  tool: string;
  options: Record<string, unknown>;
}

export interface WorkflowPreset {
  id: string;
  name: string;
  description: string;
  steps: WorkflowStep[];
}

export const WORKFLOW_PRESETS: WorkflowPreset[] = [
  {
    id: "compress-watermark-protect",
    name: "Compress → Watermark → Protect",
    description: "Shrink, stamp confidential, then password-lock for sharing.",
    steps: [
      { tool: "compress", options: { quality: "ebook" } },
      { tool: "watermark", options: { text: "CONFIDENTIAL" } },
      { tool: "protect", options: { password: "change-me" } },
    ],
  },
  {
    id: "compress-protect",
    name: "Compress → Protect",
    description: "Smaller file size, then add an open password.",
    steps: [
      { tool: "compress", options: { quality: "ebook" } },
      { tool: "protect", options: { password: "change-me" } },
    ],
  },
  {
    id: "watermark-protect",
    name: "Watermark → Protect",
    description: "Add a draft/confidential stamp, then lock the PDF.",
    steps: [
      { tool: "watermark", options: { text: "DRAFT" } },
      { tool: "protect", options: { password: "change-me" } },
    ],
  },
  {
    id: "page-numbers-protect",
    name: "Page Numbers → Protect",
    description: "Number pages, then password-protect the result.",
    steps: [
      { tool: "page-numbers", options: { position: "bottom-center" } },
      { tool: "protect", options: { password: "change-me" } },
    ],
  },
  {
    id: "rotate-compress",
    name: "Rotate → Compress",
    description: "Fix landscape scans, then reduce file size.",
    steps: [
      { tool: "rotate", options: { angle: 90 } },
      { tool: "compress", options: { quality: "ebook" } },
    ],
  },
  {
    id: "rotate-watermark",
    name: "Rotate → Watermark",
    description: "Rotate pages, then add a visible watermark.",
    steps: [
      { tool: "rotate", options: { angle: 90 } },
      { tool: "watermark", options: { text: "SCANNED COPY" } },
    ],
  },
  {
    id: "repair-compress",
    name: "Repair → Compress",
    description: "Try to fix a damaged PDF, then compress it.",
    steps: [
      { tool: "repair", options: {} },
      { tool: "compress", options: { quality: "ebook" } },
    ],
  },
  {
    id: "crop-compress",
    name: "Crop → Compress",
    description: "Trim margins from scans, then shrink the file.",
    steps: [
      { tool: "crop", options: { margin: 20 } },
      { tool: "compress", options: { quality: "ebook" } },
    ],
  },
  {
    id: "remove-pages-compress",
    name: "Remove Pages → Compress",
    description: "Drop cover pages (edit page list in JSON), then compress.",
    steps: [
      { tool: "remove-pages", options: { removePages: [1] } },
      { tool: "compress", options: { quality: "ebook" } },
    ],
  },
  {
    id: "compress-watermark",
    name: "Compress → Watermark",
    description: "Light two-step prep before emailing a document.",
    steps: [
      { tool: "compress", options: { quality: "ebook" } },
      { tool: "watermark", options: { text: "FOR REVIEW" } },
    ],
  },
  {
    id: "ocr-compress",
    name: "OCR → Compress",
    description: "Make a scan searchable, then compress (requires Tesseract).",
    steps: [
      { tool: "ocr", options: {} },
      { tool: "compress", options: { quality: "ebook" } },
    ],
  },
  {
    id: "unlock-compress",
    name: "Unlock → Compress",
    description: "Remove a password you know, then re-compress.",
    steps: [
      { tool: "unlock", options: { password: "current-password" } },
      { tool: "compress", options: { quality: "ebook" } },
    ],
  },
];

export function getWorkflowPreset(id: string): WorkflowPreset | undefined {
  return WORKFLOW_PRESETS.find((p) => p.id === id);
}
