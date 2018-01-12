import pygame
from collections import deque

BLACK = (0, 0, 0)
WHITE = (255, 255, 255)
RED = (255, 0, 0)
BLUE = (0, 0, 255)
GREEN = (0, 255, 0)
AQUA = (0, 255, 255)
PURPLE = (255, 0, 255)
YELLOW = (255, 255, 0)
COMMODORE = (158,150,242)

class Canvas:

    def __init__(self, size=16):

        self.surface = Element(size,size,0,0)
        self.size = size
        self.pixels = [None] * size               # holds actual data to write
        for y in range(size):
            self.pixels[y] = [None] * size
        self.new()

    def new(self, color=BLACK):

        for y in range(self.size):
            for x in range(self.size):
                self.pixels[y][x] = color

class Element(pygame.sprite.Sprite):

    def __init__(self, width, height, x=0, y=0, type='static'):

        super().__init__()
        self.width = width
        self.height = height
        self.image = pygame.Surface((width,height))        # image to draw
        self.image.fill(BLACK)                              # default is all black
        self.rect = self.image.get_rect()
        self.rect.x = x
        self.rect.y = y
        self.type = type                                    # defines what to do in update

    @classmethod
    def fromFile(cls, filename, x, y, type='static'):
        image = pygame.image.load(filename)
        width = image.get_width()
        height = image.get_height()
        obj = cls(width, height, x, y, type)
        obj.image = image
        obj.rect = obj.image.get_rect()
        obj.rect.x = x
        obj.rect.y = y
        return obj

    def fill(self, color):
        self.image.fill(color)

    def reposition(self, x, y):
        self.rect.x = x
        self.rect.y = y

    def scaleOnto(self, image):
        self.image = pygame.transform.scale(image, (self.width, self.height))

    def update(self, *args):
        print('update is called with',self.type)
        if self.type == 'static':
            return
        elif self.type == 'preview':
            # args[0] = source surface
            self.scaleOnto(args[0])
        elif self.type == 'highlight':
            # args[0] = (x,y)
            print('repositioning....')
            self.reposition(args[0][0], args[0][1])

class History:

    LIMIT = 100

    def __init__(self):

        self.states = deque([],History.LIMIT)

    def pushState(self, state, offset):
        for i in range(offset):
            self.states.popleft()
        self.states.appendleft(state)

    def get(self, index):
        return self.states[index]

class TextBox(Element):

    pygame.init()
    pygame.display.set_mode((800, 640))

    FONT = {
        'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'H': None, 'I': None,
        'J': None, 'K': None, 'L': None, 'M': None, 'N': None, 'O': None, 'P': None, 'Q': None, 'R': None,
        'S': None, 'T': None, 'U': None, 'V': None, 'W': None, 'X': None, 'Y': None, 'Z': None, '!': None,
        '"': None, '#': None, '$': None, '%': None, '&': None, "'": None, '(': None, ')': None, '*': None,
        '+': None, ',': None, '-': None, '.': None, '/': None, "0": None, '1': None, '2': None, '3': None,
        '4': None, '5': None, '6': None, '7': None, '8': None, "9": None, ':': None, ';': None, '<': None,
        "=": None, '>': None, '?': None, ' ': None,
    }

    FONT_SET = ('A', 'B', 'C', 'D', 'E', 'F', 'G', 'H', 'I', 'J', 'K', 'L', 'M', 'N', 'O', 'P', 'Q', 'R', 'S', 'T', 'U',
                'V', 'W', 'X', 'Y', 'Z', '!', '"', '#', '$', '%', '&', "'", '(', ')', '*', '+', ',', '-', '.', '/', '0',
                '1', '2', '3', '4', '5', '6', '7', '8', '9', ':', ';', '<', '=', '>', '?', ' ')

    FONT_SURFACE = pygame.image.load("font.png").convert_alpha()

    c = 0
    for i in range(2):
        for j in range(29):
            characterSurface = pygame.Surface((8, 8), pygame.SRCALPHA, 32)
            characterSurface.blit(FONT_SURFACE, (0, 0), ((8 * j), (8 * i), 8, 8))
            FONT[FONT_SET[c]] = characterSurface
            c += 1

    def __init__(self, cWidth, cHeight, textSize, x=0, y=0):
        super().__init__(cWidth * textSize, cHeight * textSize, x, y, "textbox")
        self.textSize = textSize
        self.cWidth = cWidth
        self.cHeight = cHeight
        self.maxLen = self.cWidth * self.cHeight
        self.text = ""

    @classmethod
    def fromText(cls, text, size, x=0, y=0):
        maxX = 0
        maxY = 1
        currentX = 0
        i = 0
        while i < len(text):
            if text[i] == "\n":
                maxY += 1
                if currentX > maxX:
                    maxX = currentX
                currentX = 0
            else:
                currentX += 1
            i += 1
        if currentX > maxX:
            maxX = currentX
        obj = cls(maxX, maxY, size, x, y)
        obj.text = text
        obj.putText()
        return obj

    def putText(self, text=None, x=0, y=0):
        if text is not None:
            self.text = text
        for c in self.text:
            if x > self.cWidth or c == '\n':
                x = 0
                y += 1
            character = pygame.transform.scale(TextBox.FONT[c], (self.textSize, self.textSize))
            self.image.blit(character, (x*self.textSize, y*self.textSize))
            x += 1

    @staticmethod
    def burnText(surface, text, size, x=0, y=0):
        """Blit a single line of text onto another surface."""
        for i, c in enumerate(text):
            offsetX = i*size
            character = pygame.transform.scale(TextBox.FONT[c], (size, size))
            surface.blit(character, (x+offsetX, y))