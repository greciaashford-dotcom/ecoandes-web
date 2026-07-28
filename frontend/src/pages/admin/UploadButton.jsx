import React, { useRef, useState } from "react";
import { Upload, Loader2 } from "lucide-react";
import { uploadFile, resolveAsset } from "../../lib/api";
import { toast } from "sonner";

// Reusable upload control. kind: 'image' | 'pdf'. Calls onUploaded({url, filename}) per file.
// Set multiple={true} to allow selecting and uploading many files at once.
export default function UploadButton({ kind = "image", label, onUploaded, testid, multiple = false }) {
  const ref = useRef(null);
  const [busy, setBusy] = useState(false);
  const [progress, setProgress] = useState({ done: 0, total: 0 });
  const accept = kind === "pdf" ? "application/pdf" : "image/*";

  const handle = async (e) => {
    const files = Array.from(e.target.files || []);
    if (files.length === 0) return;
    setBusy(true);
    setProgress({ done: 0, total: files.length });
    let ok = 0;
    const failed = [];
    for (const file of files) {
      try {
        const res = await uploadFile(file, kind);
        ok += 1;
        onUploaded(res);
      } catch (err) {
        failed.push(file.name);
        toast.error(`Error al subir ${file.name}`, { description: err.message });
      }
      setProgress((p) => ({ ...p, done: p.done + 1 }));
    }
    if (ok > 0) {
      toast.success(ok === 1 ? "Archivo subido" : `${ok} archivos subidos`, {
        description: failed.length ? `${failed.length} con error` : undefined,
      });
    }
    setBusy(false);
    setProgress({ done: 0, total: 0 });
    if (ref.current) ref.current.value = "";
  };

  const busyLabel = progress.total > 1 ? `Subiendo ${progress.done + 1 > progress.total ? progress.total : progress.done + 1}/${progress.total}\u2026` : "Subiendo\u2026";

  return (
    <>
      <button
        type="button"
        onClick={() => ref.current?.click()}
        disabled={busy}
        data-testid={testid}
        className="inline-flex items-center gap-2 text-xs uppercase tracking-[0.16em] px-3 py-2 rounded-sm border border-bone-200 bg-white text-ink hover:border-sage-500 transition-colors disabled:opacity-60"
      >
        {busy ? <Loader2 size={14} className="animate-spin" /> : <Upload size={14} />} {busy ? busyLabel : (label || "Subir")}
      </button>
      <input ref={ref} type="file" accept={accept} multiple={multiple} onChange={handle} className="hidden" />
    </>
  );
}

export { resolveAsset };
