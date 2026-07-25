"""File upload (admin) + public file serving via Emergent Object Storage."""
import logging

from fastapi import APIRouter, Depends, File, Form, HTTPException, UploadFile
from fastapi.responses import Response

from core.auth import require_admin
from core.storage import IMAGE_EXTS, get_object, upload_bytes

logger = logging.getLogger("ecoandes.files")

router = APIRouter(prefix="/api", tags=["files"])

MAX_IMAGE = 8 * 1024 * 1024     # 8 MB
MAX_PDF = 20 * 1024 * 1024      # 20 MB


@router.post("/admin/uploads", dependencies=[Depends(require_admin)])
async def admin_upload(file: UploadFile = File(...), kind: str = Form("image")):
    filename = file.filename or "file"
    ext = filename.rsplit(".", 1)[-1].lower() if "." in filename else ""
    data = await file.read()

    if kind == "pdf":
        if ext != "pdf":
            raise HTTPException(status_code=400, detail="Solo se permiten archivos PDF")
        if len(data) > MAX_PDF:
            raise HTTPException(status_code=400, detail="PDF demasiado grande (máx 20 MB)")
    else:
        if ext not in IMAGE_EXTS:
            raise HTTPException(status_code=400, detail="Formato de imagen no soportado")
        if len(data) > MAX_IMAGE:
            raise HTTPException(status_code=400, detail="Imagen demasiado grande (máx 8 MB)")

    try:
        info = upload_bytes(data, filename, kind="pdf" if kind == "pdf" else "image")
    except Exception as e:  # noqa: BLE001
        logger.exception("upload failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Error al subir: {e}")

    from core.config import db
    from datetime import datetime, timezone
    import uuid

    await db.files.insert_one(
        {
            "id": str(uuid.uuid4()),
            "storage_path": info["storage_path"],
            "original_filename": info["original_filename"],
            "content_type": info["content_type"],
            "size": info["size"],
            "is_deleted": False,
            "created_at": datetime.now(timezone.utc).isoformat(),
        }
    )
    # Public URL routed through this backend
    return {
        "url": f"/api/files/{info['storage_path']}",
        "storage_path": info["storage_path"],
        "filename": info["original_filename"],
        "content_type": info["content_type"],
    }


@router.get("/files/{path:path}")
async def serve_file(path: str):
    """Public serving of catalog assets (images + tech sheets)."""
    from core.config import db

    record = await db.files.find_one({"storage_path": path, "is_deleted": False})
    if record is None:
        # If a record exists but is soft-deleted, stop serving it
        deleted = await db.files.find_one({"storage_path": path, "is_deleted": True})
        if deleted:
            raise HTTPException(status_code=404, detail="Archivo no encontrado")
    try:
        data, content_type = get_object(path)
    except Exception:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    ct = (record or {}).get("content_type") or content_type
    return Response(
        content=data,
        media_type=ct,
        headers={"Cache-Control": "public, max-age=86400"},
    )


# ---------- Admin: media library ----------
@router.get("/admin/files", dependencies=[Depends(require_admin)])
async def list_files(kind: str = ""):
    """List uploaded files (DB is the source of truth, per storage playbook)."""
    from core.config import db

    query = {"is_deleted": False}
    if kind == "image":
        query["content_type"] = {"$regex": "^image/"}
    elif kind == "pdf":
        query["content_type"] = "application/pdf"
    files = (
        await db.files.find(query, {"_id": 0})
        .sort("created_at", -1)
        .to_list(1000)
    )
    for f in files:
        f["url"] = f"/api/files/{f['storage_path']}"
    return {"files": files, "total": len(files)}


@router.delete("/admin/files/{file_id}", dependencies=[Depends(require_admin)])
async def soft_delete_file(file_id: str):
    """Soft-delete (storage has no delete API; DB flag hides the file)."""
    from core.config import db

    res = await db.files.update_one({"id": file_id}, {"$set": {"is_deleted": True}})
    if res.matched_count == 0:
        raise HTTPException(status_code=404, detail="Archivo no encontrado")
    return {"ok": True}
