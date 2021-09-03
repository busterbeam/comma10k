#!/usr/bin/env python3
from os import rename, listdir

if __name__ == "__main__":
  sa_imgs = sorted([x for x in listdir("imgs") if x.startswith("sa")])
  total = len(sa_imgs)
  
  for num, filename in enumerate(sa_imgs, start=1):
    # shouldn't this be 04 and not just 4 -----VVVVV
    print("\x1b[2K", f"Renamed {num/total:.0%} of the files", end='\r')
    rename(f"imgs/{filename}", f"imgs/{5000+num:4}_{filename[8:]}")
    rename(f"masks/{filename}", f"masks/{5000+num:4}_{filename[8:]}")

