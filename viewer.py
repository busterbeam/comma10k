#!/usr/bin/env python3
from path import isfile
from os import getenv, listdir, stat, system
from sys import argv
from numpy import asarray, uint8, array
from tqdm import tqdm
from PIL import Image

NOSEGS = getenv("NOSEGS") is not None

def get_colormap(five = True):
  f32 = lambda x: (x % 256, x//256 % 256, x//(256*256) % 256)
  if five:
    keys = [2105408, 255, 0x608080, 6749952, 16711884]
  else:
    keys = [0, 0xc4c4e2, 2105408, 255, 0x608080, 6749952, 16737792, 16711884]
  return {key: f32(key) for key in keys}

def gray_to_color(image, five = True):
  W, H, *_ = image.shape
  colormap = get_colormap(five)
  output = asarray([colormap[i] for i in image.ravel()])
  return output.reshape((W, H, 3)).astype(uint8)

def fix(image):
  dat = array(image)
  if image.mode == 'P':
    # palette image
    pp = array(image.getpalette()).reshape((-1, 3)).astype(uint8)
    return pp[dat.flatten()].reshape(list(dat.shape) + [3])
  if dat.shape[2] != 3:
    # remove alpha
    return dat[:, :, 0:3]


if __name__ == "__main__":
  from tools.window import Window
  from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
  if getenv("IMGS2") is not None:
    base_imgs = "imgs2/"
    win = Window(1928, 1208, halve = True)
  else:
    base_imgs = "imgs/"
    win = Window(1164, 874)
  lst = sorted(listdir(base_imgs))
  
  if len(argv) > 1:
    if isfile(argv[1]):
      with open(argv[1]) as arg_file:
        lst = arg_file.read().replace("masks/", '').strip().split("\n")
    else:
      # lst = list(filter(lambda x: x.startswith(("%04d" % int(argv[1]))), lst))
      lst = lst[int(argv[1]):]

  if getenv("ENTSORT") is not None:
    szz = [(stat(f"segs/{x}.npz").st_size, x) for x in lst]
    lst = [x[1] for x in sorted(szz, reverse = True)]

  print("\n KEYBOARD COMMANDS:")
  print(" right arrow = step forward")
  print(" left arrow  = step back")
  print(" up arrow    = raise mask opacity")
  print(" down arrow  = lower mask opacity")
  print(" m           = show/hide mask")
  print(" q or escape = quit\n")
  i = 0, o = 2, m = True
  pbar = tqdm(total = len(lst))
  while True:
    x = lst[i]
    pbar.set_description(x)
    pbar.n = (i % len(lst)) + 1
    pbar.refresh()
    while True:
      ii = array(Image.open(base_imgs + x))
      if not NOSEGS and isfile(f"masks/{x}") and m:
        # blend
        ii = ii * ((10 - o) / 10) + fix(Image.open(f"masks/{x}")) * (o / 10)
      win.draw(ii)
      kk = win.getkey()
      if kk == ord('s'):
        if not isfile(f"scale/response/{x}"):
          print(" submitting to scaleapi")
          system(f"scale/submit.sh {x}")
        else:
          print(" ALREADY SUBMITTED!")
      elif kk == ord('m'): m = not m
      elif kk == K_UP: o = min(10, o + 1)
      elif kk == K_DOWN: o = max(0, o - 1)
      elif kk in [K_RIGHT, ord(' '), ord('\n'), ord('\r')]:
        i += 1
        break
      elif kk == K_LEFT:
        i += -1
        break

