from typing import Optional

from fastapi import APIRouter, HTTPException
from nap.db.models import Project
from pydantic import BaseModel

router = APIRouter(prefix="/projects")


class ProjectCreate(BaseModel):
    name: str
    description: Optional[str] = None


class ProjectUpdate(BaseModel):
    name: Optional[str] = None
    description: Optional[str] = None


class ProjectResponse(BaseModel):
    uuid: str
    name: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


def _to_response(p: Project) -> ProjectResponse:
    return ProjectResponse(
        uuid=p.uuid,
        name=p.name,
        description=p.description,
        created_at=p.created_at.isoformat(),
        updated_at=p.updated_at.isoformat(),
    )


@router.get("")
async def list_projects():
    projects = Project.query()
    return {"projects": [_to_response(p) for p in projects]}


@router.get("/{uuid}")
async def get_project(uuid: str):
    project = Project.get_by_uuid(uuid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    return _to_response(project)


@router.post("", status_code=201)
async def create_project(body: ProjectCreate):
    project = Project(name=body.name, description=body.description)
    project.create()
    return _to_response(project)


@router.put("/{uuid}")
async def update_project(uuid: str, body: ProjectUpdate):
    project = Project.get_by_uuid(uuid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")

    if body.name is not None:
        project.name = body.name
    if body.description is not None:
        project.description = body.description

    project.update()
    return _to_response(project)


@router.delete("/{uuid}", status_code=204)
async def delete_project(uuid: str):
    project = Project.get_by_uuid(uuid)
    if not project:
        raise HTTPException(status_code=404, detail="Project not found")
    project.delete()
