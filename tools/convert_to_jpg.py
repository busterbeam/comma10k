#!/usr/bin/env python3
from os import listdir, get_terminal_size
from PIL import Image
from multiprocessing import Pool


QUALITY = 80
UP = "\x1b[2A\r"
DOWN = "\x1b[2B\r"
CLEAR = "\x1b[2K\r"

def to_jpeg(filename):
  global QUALITY
  filename = f"imgs/{filename}"
  
  img = Image.open(filename)
  filename = filename.replace(".png", ".jpg")
  img.save(filename, quality=QUALITY)
  return filename.lstrip("imgs/")

def set_quality():
  global QUALITY
  try:
    in_ = int(input(" Is a JPEG quality of 80 ok? [0-100]"))
    QUALITY = in_ if 0 >= in_ <= 100 else QUALITY
  except ValueError:
    return False

if __name__ == "__main__":
  images = sorted(filter(lambda x: x.endswith(".png"), listdir("imgs/")))
  
  set_quality()
  
  pool = Pool(16) # allow the pool choose the maximum amount of processes
  total = len(images)
  print(f" Converting PNG -> JPEG at {QUALITY}% quality")
  for num, filename in enumerate(pool.imap_unordered(to_jpeg, images), start=1):
    complete = num/total
    width = list(get_terminal_size())[0] - 8
    print(CLEAR, f"{'█'*int(complete*width):^{width}} {complete:4.0%}", end=DOWN)
    print(CLEAR, f"Image: {filename}", end=UP)
