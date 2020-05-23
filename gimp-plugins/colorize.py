from _util import add_gimpenv_to_pythonpath, tqdm_as_gimp_progress

add_gimpenv_to_pythonpath()

from gimpfu import *
import numpy as np
import torch
import torch.hub
from PIL import Image


@tqdm_as_gimp_progress("Downloading model")
def load_model(device):
    G = torch.hub.load('valgur/neural-colorization:pytorch', 'generator',
                       pretrained=True, map_location=device)
    G.to(device)
    return G


def yuv2rgb(yuv):
    yuv_from_rgb = np.array([
        [0.299, 0.587, 0.114],
        [-0.14714119, -0.28886916, 0.43601035],
        [0.61497538, -0.51496512, -0.10001026]
    ])
    rgb_from_yuv = np.linalg.inv(yuv_from_rgb)
    return np.dot(yuv, rgb_from_yuv.T.copy())


@torch.no_grad()
def getcolor(input_image):
    device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
    G = load_model(device)

    input_image = input_image[..., 0]
    H, W = input_image.shape
    infimg = input_image[None, None, ...].astype(np.float32) / 255.
    img_variable = torch.from_numpy(infimg) - 0.5
    img_variable = img_variable.to(device)
    res = G(img_variable)
    uv = res.cpu().numpy()[0]
    uv[0, :, :] *= 0.436
    uv[1, :, :] *= 0.615
    u = np.array(Image.fromarray(uv[0]).resize((W, H), Image.BILINEAR))[None, ...]
    v = np.array(Image.fromarray(uv[1]).resize((W, H), Image.BILINEAR))[None, ...]
    yuv = np.concatenate([infimg[0], u, v], axis=0).transpose(1, 2, 0)

    rgb = yuv2rgb(yuv * 255)
    rgb = rgb.clip(0, 255).astype(np.uint8)
    return rgb


def channelData(layer):  # convert gimp image to numpy
    region = layer.get_pixel_rgn(0, 0, layer.width, layer.height)
    pixChars = region[:, :]  # Take whole layer
    bpp = region.bpp
    return np.frombuffer(pixChars, dtype=np.uint8).reshape(layer.height, layer.width, bpp)


def createResultLayer(image, name, result):
    rlBytes = np.uint8(result).tobytes()
    rl = gimp.Layer(image, name, image.width, image.height, image.active_layer.type, 100, NORMAL_MODE)
    region = rl.get_pixel_rgn(0, 0, rl.width, rl.height, True)
    region[:, :] = rlBytes
    image.add_layer(rl, 0)
    gimp.displays_flush()


def genNewImg(name, layer_np):
    h, w, d = layer_np.shape
    img = pdb.gimp_image_new(w, h, RGB)
    display = pdb.gimp_display_new(img)

    rlBytes = np.uint8(layer_np).tobytes()
    rl = gimp.Layer(img, name, img.width, img.height, RGB, 100, NORMAL_MODE)
    region = rl.get_pixel_rgn(0, 0, rl.width, rl.height, True)
    region[:, :] = rlBytes

    pdb.gimp_image_insert_layer(img, rl, None, 0)
    gimp.displays_flush()


def colorize(img, layer):
    gimp.progress_init("Coloring " + layer.name + "...")

    imgmat = channelData(layer)
    cpy = getcolor(imgmat)

    genNewImg(layer.name + '_colored', cpy)


register(
    "colorize",
    "colorize",
    "Generate monocular disparity map based on deep learning.",
    "Kritik Soman",
    "Your",
    "2020",
    "colorize...",
    "*",  # Alternately use RGB, RGB*, GRAY*, INDEXED etc.
    [
        (PF_IMAGE, "image", "Input image", None),
        (PF_DRAWABLE, "drawable", "Input drawable", None),
    ],
    [],
    colorize, menu="<Image>/Layer/GIML-ML")

main()
