# Diffusers Inpainting API

[![Github Contributors](https://img.shields.io/github/contributors/ainize-team/diffusers-inpainting-api)](https://github.com/badges/ainize-team/diffusers-inpainting-api/contributors)
[![GitHub issues](https://img.shields.io/github/issues/ainize-team/diffusers-inpainting-api.svg)](https://github.com/ainize-team/diffusers-inpainting-api/issues)
![Github Last Commit](https://img.shields.io/github/last-commit/ainize-team/diffusers-inpainting-api)
![Github Repository Size](https://img.shields.io/github/repo-size/ainize-team/diffusers-inpainting-api)
[![GitHub Stars](https://img.shields.io/github/stars/ainize-team/diffusers-inpainting-api.svg)](https://github.com/ainize-team/diffusers-inpainting-api/stargazers)
[![GitHub Forks](https://img.shields.io/github/forks/ainize-team/diffusers-inpainting-api.svg)](https://github.com/ainize-team/diffusers-inpainting-api/network/members)
[![GitHub Watch](https://img.shields.io/github/watchers/ainize-team/diffusers-inpainting-api.svg)](https://github.com/ainize-team/diffusers-inpainting-api/watchers)

![Supported Python versions](https://img.shields.io/badge/python-3.9-brightgreen)
[![Imports](https://img.shields.io/badge/imports-isort-brightgreen)](https://pycqa.github.io/isort/)
[![Code style](https://img.shields.io/badge/code%20style-black-black)](https://black.readthedocs.io/en/stable/)
[![pre-commit](https://img.shields.io/badge/pre--commit-enabled-brightgreen?logo=pre-commit)](https://pre-commit.com/)
![Package Management](https://img.shields.io/badge/package%20management-poetry-blue)

## Description
API Server for [diffusers](https://huggingface.co/docs/diffusers/index).

## Installation
1. build docker image
```shell
git clone https://github.com/ainize-team/diffusers-inpainting-api
cd diffusers-inpainting-api
docker build -t inpainting-api .
```

2. Run Docker Image
```
docker run -d --name inpainting-api-container -p 8000:8000 \
    -e BROKER_BASE_URI=<BROKER_BASE_URI> \
    -e VHOST_NAME=<VHOST_NAME> \
    -e FIREBASE_APP_NAME=<FIREBASE_APP_NAME>  \
    -e DATABASE_URL=<DATABASE_URL> \
    -e STORAGE_BUCKET=<STORAGE_BUCKET> \
    -v <firebase_credential_dir_path>:/app/key inpainting-api
```

or

```shell
docker run -d --name inpainting-api-container -p 8000:8000 \
    --env-file .env
    -v <firebase_credential_dir_path>:/app/key inpainting-api
```

## Usage
```
curl -X 'POST' \
  'http://192.168.1.15:8003/inpaint' \
  -H 'accept: application/json' \
  -H 'Content-Type: multipart/form-data' \
  -F 'data={
  "prompt": "Face of a yellow cat, high resolution, sitting on a park bench",
  "seed": 42,
  "num_images_per_prompt": 2,
  "guidance_scale": 7.5
}' \
  -F 'image=@image.png;type=image/png' \
  -F 'mask_image=@mask_image.png;type=image/png'
```

![image](./sample_image/image.png)

![mask_iamge](./sample_image/mask_image.png)

RESULT TO DO
## License

[![Licence](https://img.shields.io/github/license/ainize-team/diffusers-inpainting-api.svg)](./LICENSE)