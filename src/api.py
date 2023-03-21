import os
import shutil
import uuid

from celery import Celery
from fastapi import APIRouter, File, HTTPException, Request, UploadFile, status
from firebase_admin import db

from enums import ResponseStatusEnum
from schemas import AsyncTaskResponse, InpaintingResponse, InpaintRequestParams
from settings import firebase_settings
from utils import get_now_timestamp, save_image_to_storage


router = APIRouter()


def process(image_path: str, mask_image_path: str, data: InpaintRequestParams, task_id: str, celery: Celery):
    req_data = data.dict()
    req_data["image_url"] = save_image_to_storage(task_id, image_path)
    req_data["mask_image_url"] = save_image_to_storage(task_id, mask_image_path)
    shutil.rmtree(task_id, ignore_errors=True)
    app_name = firebase_settings.firebase_app_name
    try:
        db.reference(f"{app_name}/tasks/{task_id}").set(
            {
                "request": {
                    "prompt": req_data["prompt"],
                    "negative_prompt": req_data["negative_prompt"],
                    "num_images_per_prompt": req_data["num_images_per_prompt"],
                    "guidance_scale": req_data["guidance_scale"],
                    "image_url": req_data["image_url"],
                    "mask_image_url": req_data["mask_image_url"],
                },
                "seed": req_data["seed"],
                "status": ResponseStatusEnum.PENDING,
                "updated_at": get_now_timestamp(),
            }
        )
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


@router.get("/tasks/{task_id}", response_model=InpaintingResponse)
async def get_task_image(task_id: str):
    try:
        ref = db.reference(f"{firebase_settings.firebase_app_name}/tasks/{task_id}")
        data = ref.get()
    except Exception as e:
        raise HTTPException(status_code=status.HTTP_500_INTERNAL_SERVER_ERROR, detail=f"FireBaseError({task_id}): {e}")
    if data is None:
        raise HTTPException(status_code=status.HTTP_400_BAD_REQUEST, detail=f"Task ID({task_id}) not found")
    if data["status"] == ResponseStatusEnum.ERROR:
        return InpaintingResponse(
            status=data["status"],
            updated_at=data["updated_at"],
            result=data["error"]["error_message"],
        )
    return InpaintingResponse(
        status=data["status"],
        updated_at=data["updated_at"],
        result={f"{i}": data["response"][i] for i in range(len(data["response"]))}
        if data["status"] == ResponseStatusEnum.COMPLETED
        else None,
    )
