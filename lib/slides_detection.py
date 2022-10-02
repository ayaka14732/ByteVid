import matplotlib
import matplotlib.pyplot as plt
import numpy as np
import os
from PIL import Image
import torch
from typing import Optional

from models.experimental import attempt_load
from utils.datasets import LoadImages
from utils.general import non_max_suppression, scale_coords, xyxy2xywh
from utils.torch_utils import select_device, TracedModel

weights_path = 'best.pt'
device = select_device('0' if torch.cuda.is_available() else 'cpu')

imgsz = 640

half = device.type != 'cpu'  # half precision only supported on CUDA
model = attempt_load(weights=[weights_path], map_location=device)  # load FP32 model
model = TracedModel(model, device, imgsz)
if half:
    model.half()  # to FP16
stride = int(model.stride.max())  # model stride

def load_img_for_model(img_path):
    dataset = LoadImages(img_path, img_size=imgsz)

    path, img, im0s, vid_cap = next(iter(dataset))

    img = torch.from_numpy(img).to(device)
    img = img.half() if half else img.float()  # uint8 to fp16/32
    img /= 255.0  # 0 - 255 to 0.0 - 1.0
    if img.ndimension() == 3:
        img = img.unsqueeze(0)

    return img, im0s

def detect(img, im0s) -> Optional[list]:
    with torch.no_grad():
        pred = model(img, augment=False)[0]
        pred = non_max_suppression(pred, 0.25, 0.45, classes=None, agnostic=False)

        # Process detections
        for i, det in enumerate(pred):  # detections per image
            im0 = im0s

            gn = torch.tensor(im0.shape)[[1, 0, 1, 0]]  # normalization gain whwh
            if len(det):
                # Rescale boxes from img_size to im0 size
                det[:, :4] = scale_coords(img.shape[2:], det[:, :4], im0.shape).round()

                # Write results
                result = []
                for *xyxy, conf, cls in reversed(det):
                    cls = cls.int().detach().item()
                    xywh = (xyxy2xywh(torch.tensor(xyxy).view(1, 4)) / gn).view(-1).tolist()  # normalized xywh
                    result.append((cls, tuple(xywh)))
                return result

def select_largest(areas: Optional[list]):
    if not areas:
        return None

    def key(area):
        _, (_, _, w, h) = area
        return w * h
    return max(areas, key=key)

def cut_img(img, area):
    _, (x, y, w, h) = area
    img_h, img_w, _ = img.shape

    print(img_h, img_w, x, y, w, h)

    cut_x_0 = int(img_w * x - (w * img_w / 2))
    cut_x_1 = int(img_w * x + (w * img_w / 2))
    cut_y_0 = int(img_h * y - (h * img_h / 2))
    cut_y_1 = int(img_h * y + (h * img_h / 2))

    print(cut_x_0, cut_x_1, cut_y_0, cut_y_1)

    img_cut = img[cut_y_0: cut_y_1, cut_x_0: cut_x_1]
    return img_cut

def extract_slide(img_in: str, img_out: str) -> bool:
    img_full = np.array(Image.open(img_in))

    img, im0s = load_img_for_model(img_in)
    detected_areas = detect(img, im0s)
    largest_area = select_largest(detected_areas)

    if largest_area:
        img_cut = cut_img(img_full, largest_area)
        plt.imsave(img_out, img_cut)
        return True

    return False

def extract_slides(work_dir: str, keyframe_paths: list[Optional[str]]) -> list[Optional[str]]:
    res = []
    for i, keyframe_path in enumerate(keyframe_paths):
        if keyframe_path is None:
            res.append(None)
        else:
            img_in = os.path.join(work_dir, keyframe_path)
            filename = f'extracted_{i}.png'
            img_out = os.path.join(work_dir, filename)
            is_extracted = extract_slide(img_in, img_out)
            if not is_extracted:
                res.append(None)
            else:
                res.append(filename)
    return res

if __name__ == '__main__':
    matplotlib.use('QtAgg')

    for _ in range(4):
        img_full = np.array(Image.open('000151.png'))
        plt.imshow(img_full)
        plt.show()

        img, im0s = load_img_for_model('000151.png')
        largest_area = select_largest(detect(img, im0s))

        img_cut = cut_img(img_full, largest_area)
        plt.imshow(img_cut)
        plt.show()
