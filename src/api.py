import os
import shutil
import uuid
from typing import Tuple

from celery import Celery
from fastapi import APIRouter, File, HTTPException, Request, UploadFile
from firebase_admin import db

from schemas import AsyncTaskResponse, InpaintRequestParams
from settings import firebase_settings
from utils import get_now_timestamp, save_image_to_storage
from enums import ResponseStatusEnum


router = APIRouter()


def process(image_path: str, mask_image_path: str, data: InpaintRequestParams, task_id: str, celery: Celery):
    req_data = data.dict()
    req_data["image_url"] = save_image_to_storage(task_id, image_path)
    req_data["mask_image_url"] = save_image_to_storage(task_id, mask_image_path)
    shutil.rmtree(task_id, ignore_errors=True)
    app_name = firebase_settings.firebase_app_name
    try:
        db.reference(f"{app_name}/tasks/{task_id}").set({
            "request": {
                "prompt": req_data["prompt"],
                "num_images_per_prompt": req_data["num_images_per_prompt"],
                "guidance_scale": req_data["guidance_scale"],
                "image_url": req_data["image_url"],
                "mask_image_url": req_data["mask_image_url"],
            },
            "seed": req_data["seed"],
            "status": ResponseStatusEnum.PENDING,
            "updated_at": get_now_timestamp(),
        })
    except Exception as e:
        raise Exception(f"FireBase Error : {e}")
    try:
        celery.send_task(
            name="inpaint",
            kwargs={
                "task_id": task_id,
                "data": req_data,
            },
            queue="diffusers-inpainting",
        )
    except Exception as e:
        raise Exception(f"CeleryError : {e}")


@router.post("/inpaint", response_model=AsyncTaskResponse)
async def post_inpaint(
    data: InpaintRequestParams, request: Request, image: UploadFile = File(...), mask_image: UploadFile = File(...)
) -> InpaintRequestParams:
    if image.content_type == "image/png" and mask_image.content_type == "image/png":
        now = get_now_timestamp()
        task_id = str(uuid.uuid5(uuid.NAMESPACE_OID, str(now)))
        celery: Celery = request.app.state.celery

        image_path = f"{task_id}/input.png"
        mask_image_path = f"{task_id}/input_mask.png"
        os.makedirs(task_id, exist_ok=True)
        with open(image_path, "wb") as f:
            contents = await image.read()
            f.write(contents)
        with open(mask_image_path, "wb") as f:
            contents = await mask_image.read()
            f.write(contents)
        try:
            process(image_path, mask_image_path, data, task_id, celery)
        except Exception as e:
            raise HTTPException(status_code=500, detail=f"Server Error: {e}")
        return AsyncTaskResponse(task_id=task_id, updated_at=now)
    else:
        raise HTTPException(status_code=400, detail="Only Support PNG file")
