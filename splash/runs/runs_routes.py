from attr import dataclass

from fastapi import APIRouter, Path, Security, HTTPException
from fastapi.responses import StreamingResponse
from typing import List, Optional
from pydantic import BaseModel
from splash.models.users import UserModel
from .runs_service import CatalogDoesNotExist, FrameDoesNotExist, BadFrameArgument, RunsService, RunSummary
from splash.api.auth import get_current_user

runs_router = APIRouter()


@dataclass
class Services():
    runs: RunsService


services = Services(None)


def set_runs_service(runs_svc: RunsService):
    services.runs = runs_svc


class RunMetadataModel(BaseModel):
    energy: float


@runs_router.get("", tags=["runs"], response_model=List[str])
def read_catalogs(
        current_user: UserModel = Security(get_current_user)):

    catalog_names = services.runs.list_root_catalogs()
    return catalog_names


@runs_router.get("/{catalog_name}", tags=['runs'], response_model=List[RunSummary])
def read_catalog(
            catalog_name: str = Path(..., title="name of catalog"),
            current_user: UserModel = Security(get_current_user)):
    try:
        runs = services.runs.get_runs(current_user, catalog_name)
        return runs
    except CatalogDoesNotExist as e:
        raise HTTPException(404, detail=e.args[0])

    
  


# @runs_router.get("/{catalog_name}/{run_uid}/image", tags=['runs'], response_model=RunModel)
# def read_frame(
#         catalog_name: str = Path(..., title="catalog name"),
#         run_uid: str = Path(..., title="run uid"),
#         frame: Optional[int] = 0,
#         current_user: UserModel = Security(get_current_user)):
#     try:
#         jpeg_generator = services.runs.get_image(catalog_name=catalog_name, uid=run_uid, frame=frame)
#     except FrameDoesNotExist as e:
#         raise HTTPException(400, detail=e.args[0])
#     except BadFrameArgument as e:
#         raise HTTPException(422, detail=e.args[0])

#     return StreamingResponse(jpeg_generator, media_type="image/JPEG")


@runs_router.get("/{catalog_name}/{run_uid}/metadata", tags=['runs'], response_model=RunMetadataModel)
def read_frame_metadata(
        catalog_name: str = Path(..., title="catalog name"),
        run_uid: str = Path(..., title="run uid"),
        frame: Optional[int] = 0):
    try:
        return_metadata = services.runs.get_metadata(catalog_name=catalog_name, uid=run_uid, frame=frame)
    except FrameDoesNotExist as e:
        raise HTTPException(400, detail=e.args[0])
    except BadFrameArgument as e:
        raise HTTPException(422, detail=e.args[0])

    return RunMetadataModel(energy=return_metadata.get('/entry/instrument/monochromator/energy'))