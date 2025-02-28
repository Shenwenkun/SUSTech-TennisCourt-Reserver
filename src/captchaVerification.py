import random
import numpy as np
import imageio.v3 as iio
import requests
from scipy.cluster.vq import kmeans, vq

from AES_Util import *
from Load_json import *


class Point:
    def __init__(self, x: float, y: float):
        self.x = x
        self.y = y

    def toString(self) -> str:
        return '{"x":' + str(self.x) + ',"y":' + str(self.y) + '}'


class BufferedImage:
    def __init__(self, image_path: str):
        self.image = iio.imread(image_path)
        if self.image is None:
            raise ValueError("Image file could not be loaded.")
        self.height, self.width = self.image.shape[:2]


def decode_and_save_image(base64_string, filename):
    with open(filename, 'wb') as f:
        f.write(base64.b64decode(base64_string))


def get(config):
    url = "https://reservation.sustech.edu.cn/api/captcha/get"
    headers = config["headers"]
    payload = config["captcha_payload"]
    point = None
    secretKey = None
    token = None

    while point is None:
        response = requests.post(url, headers=headers, data=json.dumps(payload))

        decode_and_save_image(response.json()["repData"]["originalImageBase64"], "original_image.png")
        decode_and_save_image(response.json()["repData"]["jigsawImageBase64"], "jigsaw_image.png")
        secretKey = response.json()["repData"]["secretKey"]
        token = response.json()["repData"]["token"]

        jigsaw = iio.imread("jigsaw_image.png")
        if jigsaw.shape[-1] == 4:
            alpha_channel = jigsaw[:, :, 3]
        else:
            raise ValueError("Image does not have an alpha channel.")
        non_transparent_pixels = np.argwhere(alpha_channel > 0)
        if non_transparent_pixels.size > 0:
            top_left_jigsaw = tuple(non_transparent_pixels.min(axis=0))
        else:
            raise ValueError("No non-transparent pixels found in the image.")

        original = iio.imread("original_image.png")
        if original.shape[-1] == 4:
            original = original[:, :, :3]
        white_threshold = np.array([250, 250, 250])
        white_pixels = np.all(original >= white_threshold, axis=-1)
        nonzero_coords = np.argwhere(white_pixels)
        if len(nonzero_coords) >= 3:
            centroids, _ = kmeans(nonzero_coords.astype(float), 3)
            labels, _ = vq(nonzero_coords.astype(float), centroids)
            top_left_corners = []
            for i in range(3):
                cluster_points = nonzero_coords[labels == i]
                top_left = tuple(cluster_points.min(axis=0))
                if top_left[0] == top_left_jigsaw[0]:
                    point = Point(top_left[1], top_left[0])
                top_left_corners.append(top_left)
        else:
            raise ValueError("Could not detect three separate white-bordered regions.")

    point.x = point.x + random.random()
    return point, secretKey, token

def check(config, point, secretKey, token):
    point.y = 5
    url = "https://reservation.sustech.edu.cn/api/captcha/check"
    headers = config["headers"]
    pointJson = str(aes_encrypt_by_bytes(point.toString(), secretKey), encoding='utf-8')
    payload = {
        "captchaType": str("blockPuzzle"),
        "pointJson": str(pointJson),
        "token": str(token)
    }

    response = requests.post(url, headers=headers, data=json.dumps(payload))
    if not response.json()["success"]:
        print("Captcha verification failed!")
        return None
    else:
        print("Captcha verification passed!")
        return aes_encrypt_by_bytes(token + "---" + point.toString(), secretKey)


def Verification():
    config = get_config()
    while True:
        point, secretKey, token = get(config)
        verification = check(config, point, secretKey, token)
        get(config)
        if verification is None:
            continue
        return str(verification)


if __name__ == "__main__":
    Verification()
