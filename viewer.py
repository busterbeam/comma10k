#!/usr/bin/env python3
from os import getenv, listdir, stat, system
from os.path import isfile
from sys import argv
from numpy import asarray, uint8, array
from tqdm import tqdm
from PIL import Image

NOSEGS = getenv("NOSEGS") is not None

def get_colormap(five=True):
  f32 = lambda x: (x % 256, x//256 % 256, x//(256*256) % 256)
  if five:
    key = [2105408, 255, 0x608080, 6749952, 16711884]
  else:
    key = [0, 0xc4c4e2, 2105408, 255, 0x608080, 6749952, 16737792, 16711884]
  return {n: f32(k) for n, k in enumerate(key))}

def gray_to_color(image, five=True):
  W,H = image.shape[0:2]
  colormap = get_colormap(five)
  c = image.ravel()
  output = asarray([colormap[i] for i in c])
  return output.reshape((W, H, 3)).astype(uint8)

def fix(im):
  dat = array(im)
  if im.mode == 'P':
    # palette image
    pp = array(im.getpalette()).reshape((-1, 3)).astype(uint8)
    dat = pp[dat.flatten()].reshape(list(dat.shape)+[3])

  if dat.shape[2] != 3:
    # remove alpha
    dat = dat[:, :, 0:3]
  return dat

def init_window():
  from tools.window import Window
  if getenv("IMGS2") is not None:
    return Window(1928, 1208, halve=True)
  else:
    return Window(1164, 874)

def init_directory(base_imgs):
  lst = sorted(listdir(base_imgs))
  if len(argv) > 1:
    if isfile(argv[1]):
      with open(argv[1]) as list_file:
        lst = list_file.read().replace("masks/", '').strip().split('\n')
    else:
      # lst = list(filter(lambda x: x.startswith(("%04d" % int(argv[1]))), lst))
      lst = lst[int(argv[1]):]
  if getenv("ENTSORT") is not None:
    lst = sorted(
      lst, key=lambda x: int(stat(f"segs/{x}.npz").st_size), reverse=True)
  return lst

def display_instructions():
  print("\n ⌨️  KEYBOARD COMMANDS:",
         " ➡️  = step forward",
         " ⬅️  = step back",
         " ⬆️  = raise mask opacity",
         " ⬇️  = lower mask opacity",
         " m  = show/hide mask",
         " s  = submit to scale API",
         " q or ESC = quit\n", sep='\n')

if __name__ == "__main__":
  from pygame import K_UP, K_DOWN, K_LEFT, K_RIGHT
  win = init_window()
  base_imgs = "imgs2/" if getenv("IMGS2") is not None else "imgs/"
  filenames = init_directory(base_imgs)
  display_instructions()
  
  next_keys = [K_RIGHT, ord(' '), ord('\n'), ord('\r')]
  index = 0
  o = 2
  mask_state = True
  progress_bar = tqdm(total=len(filenames))
  while True:
    filename = filenames[index]
    progress_bar.set_description(filename)
    progress_bar.n = (index % len(filenames)) + 1
    progress_bar.refresh()
    while True:
      ii = array(Image.open(f"{base_imgs}{filename}"))
      if not NOSEGS and isfile(f"masks/{filename}") and mask_state:
        segi = fix(Image.open(f"masks/{filename}"))
        # blend
        ii = ii * ((10 - o) / 10) + segi * (o / 10)
      win.draw(ii)
      key_press = win.getkey()
      if key_press == ord('s'):
        if not isfile(f"scale/response/{filename}"):
          print("submitting to scaleapi")
          system(f"scale/submit.sh {filename}")
        else:
          print("ALREADY SUBMITTED!")
      elif key_press == ord('m'):
        mask_state = not mask_state
      elif key_press == K_UP:
        o = min(10, o + 1)
      elif key_press == K_DOWN:
        o = max(0, o - 1)
      elif key_press in next_keys:
        index += 1
        break
      elif key_press == K_LEFT:
        index -= 1
        break
