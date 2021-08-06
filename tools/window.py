from sys import exit
from pygame import quit, QUIT, KEYDOWN, MOUSEBUTTONDOWN
from pygame.mouse import get_pos
from pygame.display import set_mode, init, set_caption, flip
from pygame.event import pump, wait, get
from pygame.surfarray import blit_array
from cv2 import resize

class Window():
  def __init__(self, w, h, caption = "window", double = False, halve = False):
    self.w = w
    self.h = h
    init(), set_caption(caption)
    self.double = double
    self.halve = halve
    if self.double:
      self.screen = set_mode((w * 2, h * 2))
    elif self.halve:
      self.screen = set_mode((w // 2, h // 2))
    else:
      self.screen = set_mode((w, h))

  def draw(self, out):
    pump()
    if self.double:
      blit_array(self.screen, resize(out, (self.w*2, self.h*2)).swapaxes(0, 1))
    elif self.halve:
      blit_array(self.screen, resize(out, (self.w//2, self.h//2)).swapaxes(0, 1))
    else:
      blit_array(self.screen, out.swapaxes(0, 1))
    flip()

  def getkey(self):
    while True:
      event = wait()
      if event.type == QUIT:
        quit(), exit()
      if event.type == KEYDOWN:
        return event.key

  def getclick(self):
    for event in get():
      if event.type == MOUSEBUTTONDOWN:
        return get_pos()

if __name__ == "__main__":
  from numpy import zeros, uint8
  window = Window(200, 200, double = True)
  image = zeros((200, 200, 3), uint8)
  while True:
    print("draw")
    image += 1
    window.draw(image)
