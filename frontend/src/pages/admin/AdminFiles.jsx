import React, { useEffect, useState } from "react";
import { FolderOpen, FileText, ImageIcon, Copy, Trash2, RefreshCcw, Check, Eye } from "lucide-react";
import { api, resolveAsset } from "../../lib/api";
import { toast } from "sonner";
import UploadButton from "./UploadButton";

function fmtSize(bytes) {
  if (!bytes && bytes !== 0) return "—";
  if (bytes < 1024) return `${bytes} B`;
  if (bytes < 1024 * 1024) return `${(bytes / 1024).toFixed(1)} KB`;
  return `${(bytes / (1024 * 1024)).toFixed(1)} MB`;
}

function fmtDate(iso) {
  if (!iso) return "—";
  try {
    return new Date(iso).toLocaleDateString("es-ES", { day: "2-digit", month: "2-digit", year: "numeric" });
  } catch {
    return iso.slice(0, 10);
  }
}

export default function AdminFiles() {
  const [files, setFiles] = useState([]);
  const [loading, setLoading] = useState(true);
  const [filter, setFilter] = useState("");
  const [copiedId, setCopiedId] = useState(null);

  const load = () => {
    setLoading(true);
    api
      .get("/admin/files", { params: filter ? { kind: filter } : {} })
      .then(({ data }) => setFiles(data.files || []))
      .catch(() => toast.error("Error al cargar archivos"))
      .finally(() => setLoading(false));
  };

  useEffect(load, [filter]);

  const copyUrl = (f) => {
    const full = resolveAsset(f.url);
    navigator.clipboard.writeText(full).then(() => {
      setCopiedId(f.id);
      toast.success("URL copiada");
      setTimeout(() => setCopiedId(null), 1800);
    });
  };

  const deleteFile = async (f) => {
    if (!window.confirm(`¿Eliminar "${f.original_filename}"? Dejará de servirse públicamente.`)) return;
    try {
      await api.delete(`/admin/files/${f.id}`);
      setFiles((prev) => prev.filter((x) => x.id !== f.id));
      toast.success("Archivo eliminado");
    } catch {
      toast.error("Error al eliminar");
    }
  };

  const isImage = (f) => (f.content_type || "").startsWith("image/");

  const tabs = [
    { key: "", label: "Todos" },
    { key: "image", label: "Imágenes" },
    { key: "pdf", label: "PDFs" },
  ];

  return (
    <div data-testid="admin-files-page">
      <div className="flex flex-wrap items-end justify-between gap-4 mb-8">
        <div>
          <div className="overline">Almacenamiento</div>
          <h1 className="font-heading text-3xl font-light">Archivos y Medios</h1>
          <p className="text-ink-soft text-sm mt-2 max-w-2xl">
            Biblioteca de medios de la tienda: imágenes de productos, portada y fichas técnicas (PDF).
            Sube archivos y copia su URL para usarla donde la necesites.
          </p>
        </div>
        <div className="flex gap-3 items-center">
          <button onClick={load} className="btn-outline inline-flex items-center gap-2" data-testid="files-refresh">
            <RefreshCcw size={15} /> Actualizar
          </button>
          <UploadButton kind="image" label="Subir imagen" testid="files-upload-image" onUploaded={() => load()} />
          <UploadButton kind="pdf" label="Subir PDF" testid="files-upload-pdf" onUploaded={() => load()} />
        </div>
      </div>

      <div className="flex gap-2 mb-6">
        {tabs.map((tb) => (
          <button
            key={tb.key}
            onClick={() => setFilter(tb.key)}
            data-testid={`files-filter-${tb.key || "all"}`}
            className={`text-xs uppercase tracking-[0.16em] px-4 py-2 rounded-full border transition ${
              filter === tb.key
                ? "bg-sage-600 text-white border-sage-600"
                : "bg-white text-ink-soft border-bone-200 hover:border-sage-500"
            }`}
          >
            {tb.label}
          </button>
        ))}
        <span className="ml-auto text-sm text-ink-soft self-center" data-testid="files-count">
          {files.length} archivo{files.length !== 1 ? "s" : ""}
        </span>
      </div>

      {loading ? (
        <div className="py-20 text-center text-ink-soft">Cargando…</div>
      ) : files.length === 0 ? (
        <div className="bg-white border border-bone-200 rounded-xl py-20 text-center text-ink-soft" data-testid="files-empty">
          <FolderOpen size={32} className="mx-auto mb-4 text-bone-300" />
          Todavía no hay archivos. Sube imágenes o PDFs con los botones de arriba.
        </div>
      ) : (
        <div className="grid grid-cols-2 sm:grid-cols-3 lg:grid-cols-4 xl:grid-cols-5 gap-4">
          {files.map((f) => (
            <div
              key={f.id}
              className="group bg-white border border-bone-200 rounded-xl overflow-hidden hover:shadow-sm transition"
              data-testid={`file-card-${f.id}`}
            >
              <div className="aspect-square bg-bone-100 flex items-center justify-center overflow-hidden relative">
                {isImage(f) ? (
                  <img
                    src={resolveAsset(f.url)}
                    alt={f.original_filename}
                    loading="lazy"
                    className="w-full h-full object-contain p-2"
                  />
                ) : (
                  <FileText size={40} className="text-terracotta" />
                )}
                <div className="absolute top-2 left-2">
                  <span className="inline-flex items-center gap-1 bg-white/90 backdrop-blur text-[10px] uppercase tracking-wide text-ink-soft px-2 py-0.5 rounded-full border border-bone-200">
                    {isImage(f) ? <ImageIcon size={10} /> : <FileText size={10} />}
                    {isImage(f) ? "Imagen" : "PDF"}
                  </span>
                </div>
              </div>
              <div className="p-3">
                <div className="text-xs text-ink truncate" title={f.original_filename}>{f.original_filename}</div>
                <div className="text-[11px] text-ink-muted mt-0.5">{fmtSize(f.size)} · {fmtDate(f.created_at)}</div>
                <div className="flex items-center gap-1.5 mt-2.5">
                  <a
                    href={resolveAsset(f.url)}
                    target="_blank"
                    rel="noopener noreferrer"
                    data-testid={`file-view-${f.id}`}
                    className="flex-1 inline-flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide px-2 py-1.5 rounded-sm border border-sage-500 text-sage-700 hover:bg-sage-50 transition"
                  >
                    <Eye size={12} /> Ver Documento
                  </a>
                  <button
                    onClick={() => copyUrl(f)}
                    data-testid={`file-copy-${f.id}`}
                    className="inline-flex items-center justify-center gap-1.5 text-[11px] uppercase tracking-wide px-2 py-1.5 rounded-sm border border-bone-200 text-ink-soft hover:border-sage-500 hover:text-sage-700 transition"
                    aria-label="Copiar URL"
                  >
                    {copiedId === f.id ? <Check size={12} className="text-sage-600" /> : <Copy size={12} />}
                  </button>
                  <button
                    onClick={() => deleteFile(f)}
                    aria-label="Eliminar"
                    data-testid={`file-delete-${f.id}`}
                    className="p-1.5 rounded-sm border border-bone-200 text-ink-muted hover:text-red-500 hover:border-red-300 transition"
                  >
                    <Trash2 size={13} />
                  </button>
                </div>
              </div>
            </div>
          ))}
        </div>
      )}
    </div>
  );
}
