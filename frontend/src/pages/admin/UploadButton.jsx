import React, { useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import { uploadFile, resolveAsset } from "../../lib/api";
import { toast } from "sonner";

// Reusable upload control. kind: 'image' | 'pdf'. Calls onUploaded({url, filename}).
export default function UploadButton({ kind = "image", label, onUploaded, testid }) {
  const ref = useRef(null);
  const [busy, setBusy] = useState(false);
  const accept = kind === "pdf" ? "application/pdf" : "image/*";

  const handle = async (e) => {
    const file = e.target.files?.[0];
    if (!file) return;
    setBusy(true);
    try {
      const res = await uploadFile(file, kind);
      onUploaded(res);
      toast.success("Archivo subido");
    } catch (err) {
      toast.error("Error al subir", { description: err.message });
    } finally {
      setBusy(false);
      if (ref.current) ref.current.value = "";
    }
  };

  return (
    <>
      <button
        type="button"
        onClick={() => ref.current?.click()}
        disabled={busy}
        data-testid={testid}
        className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.16em] px-3 py-2 rounded-sm border border-bone-200 bg-white text-ink hover:border-sage-500 transition-colors disabled:opacity-60"
      >
        {busy ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />} {label || "Subir"}
      </button>
      <input ref={ref} type="file" accept={accept} onChange={handle} className="hidden" />
    </>
  );
}

export { resolveAsset };
