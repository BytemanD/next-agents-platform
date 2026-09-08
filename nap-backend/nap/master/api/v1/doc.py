from fastapi import APIRouter, BackgroundTasks, File, UploadFile
from fastapi.responses import FileResponse, JSONResponse
from nap.master.manager import MANAGER

router = APIRouter(prefix="/docs")


@router.get("")
async def list_docs():
    docs = MANAGER.list_docs()
    return {"docs": docs}


@router.post("/upload")
async def upload_doc(
    file: UploadFile = File(...),
    background_tasks: BackgroundTasks = None,
):
    content = await file.read()
    doc = MANAGER.upload_doc(file.filename, content)
    background_tasks.add_task(MANAGER.parse_doc, doc.uuid)
    return {"message": "ok"}


@router.get("/download")
async def download_doc(
    path: str,
):
    if not path:
        return JSONResponse(status_code=400, content={"path is required"})
    file_path = MANAGER.get_doc_path(path)
    if not file_path:
        return JSONResponse(status_code=404, content={"file not found"})
    return FileResponse(file_path, filename=file_path.name)
