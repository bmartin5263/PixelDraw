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

class Pixel(pygame.sprite.Sprite):

    def __init__(self):

        super().__init__()
        self.image = pygame.Surface((32,32))
        self.image.fill(BLACK)
        self.rect = self.image.get_rect()

    def update(self, color):
        self.image.fill(color)

class Preview(pygame.sprite.Sprite):

    def __init__(self, size):

        super().__init__()
        self.size = size
        self.image = pygame.Surface((size, size))
        self.image.fill(AQUA)
        self.rect = self.image.get_rect()

    def update(self, surfaceImage):
        self.image = pygame.transform.scale(surfaceImage, (self.size,self.size))

class Color(pygame.sprite.Sprite):

    def __init__(self):

        super().__init__()
        self.image = pygame.Surface((26, 26))
        self.image.fill(WHITE)
        self.rect = self.image.get_rect()

    def update(self, color):
        self.image.fill(color)

class ColorHighlight(pygame.sprite.Sprite):

    def __init__(self):

        super().__init__()
        self.image = pygame.image.load("highlightcolor.png")
        self.rect = self.image.get_rect()

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

class CanvasHighlight(pygame.sprite.Sprite):

    def __init__(self):

        super().__init__()
        self.image = pygame.image.load("highlightcanvas.png")
        self.rect = self.image.get_rect()

    def update(self, x, y):
        self.rect.x = x
        self.rect.y = y

class History():

    LIMIT = 100

    def __init__(self):

        self.states = deque([],History.LIMIT)

    def pushState(self, state, offset):
        for i in range(offset):
            self.states.popleft()
        self.states.appendleft(state)

    def get(self, index):
        return self.states[index]

class PixelDraw():

    SURROUNDING = (
        (1,0),
        (0,1),
        (-1,0),
        (0,-1)
    )

    NEXT_CATEGORY_RIGHT = {
        'white' : 'red',
        'red' : 'orange',
        'orange' : 'green',
        'green' : 'blue',
        'blue' : 'purple',
        'purple' : 'white'
    }

    NEXT_CATEGORY_LEFT = {
        'white': 'purple',
        'red': 'white',
        'orange': 'red',
        'green': 'orange',
        'blue': 'green',
        'purple': 'blue'
    }

    NUMBERS = (pygame.K_0, pygame.K_1, pygame.K_2, pygame.K_3, pygame.K_4, pygame.K_5,
               pygame.K_6, pygame.K_7, pygame.K_8, pygame.K_9)

    TIMES = {
        'move' : 200,
        'undo' : 100,
        'cp' : 150
    }

    FONT_SET = ('A','B','C','D','E','F','G','H','I','J','K','L','M','N','O','P','Q','R','S','T','U',
                'V','W','X','Y','Z','!','"','#','$','%','&',"'",'(',')','*','+',',','-','.','/','0',
                '1','2','3','4','5','6','7','8','9',':',';','<','=','>','?',' ')

    FILENAME_SET = ('a','b','c','d','e','f','g','h','i','j','k','l','m','n','o','p','q','r','s','t',
                    'u','v','w','x','y','z','-','0','1','2','3','4','5','6','7','8','9','.')

    def __init__(self):
        self.x = 800
        self.y = 640
        self.screen = None
        self.clock = None
        self.complete = False

        self.saveActive = False
        self.saveName = ""

        self.history = None
        self.historyPointer = 0

        self.elapsedTime = dict(PixelDraw.TIMES)

        self.background = None
        self.backgroundRect = None
        self.saveDialogBackground = None
        self.saveDialogRect = None

        self.fontSurface = None
        self.saveNameSurface = None

        self.grid = None
        self.gridRect = None
        self.useGrid = False

        self.transparentColor = None
        self.backdropColor = None
        self.memoryColor = None

        self.categoryPointer = None         # which color type
        self.colorPointer = 0               # which color
        self.framePointer = 0               # which frame
        self.canvasPointer = (0,0)          # where on the canvas

        self.canvases = 0           # TODO multiple canvases
        self.currentCanvas = 0      # TODO multiple canvases

        self.canvas = None                                  # surface object to export
        self.canvasRectangle = None                         # positioning data
        self.canvasSprites = [None] * 16                    # individual "pixels", holds ui data
        for y in range(16):
            self.canvasSprites[y] = [None] * 16
        self.pixelGrid = [None] * 16                        # holds actual data to write
        for y in range(16):
            self.pixelGrid[y] = [None] * 16

        self.preview32 = None
        self.preview64 = None

        self.colorHighlight = None      # sprite for frame
        self.canvasHighlight = None     # sprite for frame
        self.frameHighlight = None      # sprite for frame

        self.saveTransparencyColorBox = None

        self.spriteList = None
        self.pixelList = None
        self.previewList = None
        self.colorList = None
        self.colorSprites = None
        self.specialColorList = None
        self.canvasList = None
        self.specialColorSprites = None

        self.COLORS = {}            # category : List of RGB Values

        self.COORDINATES = {
            'colorView' : (23,578),             # offset x+37
            'colorHighlight' : (20,575),        # offset x+37
            'specialColors' : (412,578),        # offset x+36
            'canvas' : (10,10),                 # offset x+32
            'size16': (538, 16),
            'size32' : (562, 63),
            'size64' : (562, 136),
            'landscape' : (664,73),             # offset x+32
            'frames' : (551, 269),              # offset x+22
            'category' : (18, 541)              # TODO
        }

        self.SAVECOORDINATES = {
            'box' : (50, 162),
            'SAVE IMAGE' : (56, 24),
            'name' : (106, 242),                # offset x+16
            'color' : (109, 285),
            'TRANSPARENCY' : (96, 128),
            'SHIFT-S TO SAVE' : (96, 168),
        }

        self.FONT = {
            'A': None, 'B': None, 'C': None, 'D': None, 'E': None, 'F': None, 'G': None, 'H': None, 'I': None,
            'J': None, 'K': None, 'L': None, 'M': None, 'N': None, 'O': None, 'P': None, 'Q': None, 'R': None,
            'S': None, 'T': None, 'U': None, 'V': None, 'W': None, 'X': None, 'Y': None, 'Z': None, '!': None,
            '"': None, '#': None, '$': None, '%': None, '&': None, "'": None, '(': None, ')': None, '*': None,
            '+': None, ',': None, '-': None, '.': None, '/': None, "0": None, '1': None, '2': None, '3': None,
            '4': None, '5': None, '6': None, '7': None, '8': None, "9": None, ':': None, ';': None, '<': None,
            "=": None, '>': None, '?': None, ' ': None,
        }

        self.CATEGORY_SURFACES = {
            'white' : None,
            'red' : None,
            'orange' : None,
            'green' : None,
            'blue' : None,
            'purple' : None
        }

    def setup(self):
        pygame.init()
        pygame.mouse.set_visible(True)
        self.screen = pygame.display.set_mode((self.x, self.y))
        self.clock = pygame.time.Clock()

        colorfile = open("colors.txt", 'r')
        lines = colorfile.readlines()
        category = ''
        for line in lines:
            split = line.split()
            if len(split) > 0:
                if split[0].isdigit():
                    rgb = (int(split[0]), int(split[1]), int(split[2]))
                    self.COLORS[category].append(rgb)
                else:
                    category = split[0].lower()
                    self.COLORS[category] = []

        self.spriteList = pygame.sprite.Group()
        self.pixelList = pygame.sprite.Group()
        self.previewList = pygame.sprite.Group()
        self.colorList = pygame.sprite.Group()
        self.canvasList = pygame.sprite.Group()
        self.specialColorList = pygame.sprite.Group()

        self.background = pygame.image.load("background.png")
        self.backgroundRect = self.background.get_rect()
        self.saveDialogBackground = pygame.image.load("save-dialog.png")
        self.saveDialogRect = self.saveDialogBackground.get_rect()
        self.saveDialogRect.x = 50
        self.saveDialogRect.y = 162
        self.grid = pygame.image.load("grid.png")
        self.gridRect = self.grid.get_rect()
        self.gridRect.x = self.COORDINATES['canvas'][0]
        self.gridRect.y = self.COORDINATES['canvas'][1]
        self.fontSurface = pygame.image.load("font.png").convert_alpha()

        c = 0
        for i in range(2):
            for j in range(29):
                characterSurface = pygame.Surface((8,8),pygame.SRCALPHA, 32)
                characterSurface.blit(self.fontSurface,(0,0),((8*j),(8*i),8,8))
                self.FONT[self.FONT_SET[c]] = characterSurface
                c += 1

        for category in self.CATEGORY_SURFACES:
            categoryUpper = category.upper()
            textLen = len(category)
            categorySurface = pygame.Surface((16*textLen, 16), pygame.SRCALPHA, 32)
            for i, c in enumerate(categoryUpper):
                enlargedText = pygame.transform.scale(self.FONT[c],(16,16))
                categorySurface.blit(enlargedText, (16*i, 0))
            self.CATEGORY_SURFACES[category] = categorySurface

        self.saveNameSurface = pygame.Surface((320, 16))
        for i,c in enumerate(['.','P','N','G']):
            enlargedText = pygame.transform.scale(self.FONT[c], (16, 16))
            self.saveNameSurface.blit(enlargedText, (16 * (16+i), 0))
        arr = pygame.PixelArray(self.saveNameSurface)
        arr.replace(WHITE, COMMODORE)
        del arr

        for string in ('TRANSPARENCY', 'SHIFT-S TO SAVE', 'SAVE IMAGE'):
            size = 16
            if string == 'SAVE IMAGE':
                size = 32
            textLen = len(string)
            stringSurface = pygame.Surface((size * textLen, size))
            for i, c in enumerate(string):
                enlargedText = pygame.transform.scale(self.FONT[c], (size, size))
                stringSurface.blit(enlargedText, (size * i, 0))
            self.saveDialogBackground.blit(stringSurface, (self.SAVECOORDINATES[string][0],self.SAVECOORDINATES[string][1]))


        self.colorSprites = []
        for i in range(10):
            color = Color()
            color.rect.x = self.COORDINATES['colorView'][0] + (37 * i)
            color.rect.y = self.COORDINATES['colorView'][1]
            self.colorList.add(color)
            self.colorSprites.append(color)

        self.specialColorSprites = []
        for i in range(3):
            color = Color()
            color.rect.x = self.COORDINATES['specialColors'][0] + (36 * i)
            color.rect.y = self.COORDINATES['specialColors'][1]
            self.specialColorList.add(color)
            self.specialColorSprites.append(color)

        self.saveTransparencyColorBox = Color()
        self.saveTransparencyColorBox.rect.x = self.SAVECOORDINATES['color'][0]
        self.saveTransparencyColorBox.rect.y = self.SAVECOORDINATES['color'][1]


        self.preview32 = Preview(32)
        self.preview32.rect.x = self.COORDINATES['size32'][0]
        self.preview32.rect.y = self.COORDINATES['size32'][1]
        self.previewList.add(self.preview32)
        self.preview64 = Preview(64)
        self.preview64.rect.x = self.COORDINATES['size64'][0]
        self.preview64.rect.y = self.COORDINATES['size64'][1]
        self.previewList.add(self.preview64)
        for y in range(3):
            for x in range(3):
                p = Preview(32)
                p.rect.x = self.COORDINATES['landscape'][0] + (32 * x)
                p.rect.y = self.COORDINATES['landscape'][1] + (32 * y)
                self.previewList.add(p)

        self.setCategoryPointer('white')
        self.setSpecialColor(0, BLACK)
        self.setSpecialColor(1, BLACK)
        self.setSpecialColor(2, BLACK)

        self.colorHighlight = ColorHighlight()
        self.setColorPointer(1, False)

        self.newCanvas()

        self.canvasHighlight = CanvasHighlight()
        self.setCanvasPointer((0,0))

        self.history = History()
        self.historyPointer = 0
        self.historyState()

    def applyPixelGrid(self, grid):
        for y in range(16):
            for x in range(16):
                self.canvasSprites[y][x].update(grid[y][x])
                self.canvas.set_at((x, y), grid[y][x])
        self.previewList.update(self.canvas)

    def bucketFill(self, coordinates, color):
        def fill(coordinates, color, fillColor):
            x = coordinates[0]
            y = coordinates[1]
            if self.pixelGrid[y][x] == fillColor:
                self.colorPixel(coordinates, color)
                for sur in PixelDraw.SURROUNDING:
                    newX = coordinates[0] + sur[0]
                    newY = coordinates[1] + sur[1]
                    if 0 <= newX < 16 and 0 <= newY < 16:
                        fill((newX, newY), color, fillColor)

        fillColor = self.pixelGrid[coordinates[1]][coordinates[0]]
        if fillColor != color:
            fill(coordinates, color, fillColor)
            self.applyPixelGrid(self.pixelGrid)
            self.historyState()

    def colorPixel(self, coordinates, color):
        x = coordinates[0]
        y = coordinates[1]
        if self.pixelGrid[y][x] == color:
            return False
        p = self.canvasSprites[y][x]
        p.update(color)
        self.pixelGrid[y][x] = color
        self.canvas.set_at((x,y), color)
        self.previewList.update(self.canvas)
        return True

    def copyColor(self, coordinates):
        x = coordinates[0]
        y = coordinates[1]
        color = self.pixelGrid[y][x]
        for category in self.COLORS:
            for i, c in enumerate(self.COLORS[category]):
                if c == color:
                    self.setCategoryPointer(category)
                    self.setColorPointer(i, True)

    def drawSprites(self):
        self.pixelList.draw(self.screen)
        self.previewList.draw(self.screen)
        self.colorList.draw(self.screen)
        self.specialColorList.draw(self.screen)
        self.canvasList.draw(self.screen)
        self.screen.blit(self.CATEGORY_SURFACES[self.categoryPointer], (self.COORDINATES['category'][0], self.COORDINATES['category'][1]))

        self.screen.blit(self.canvas, self.canvasRectangle)
        self.screen.blit(self.colorHighlight.image, self.colorHighlight.rect)
        self.screen.blit(self.canvasHighlight.image, self.canvasHighlight.rect)
        #self.screen.blit(self.frameHighlight.image, self.frameHighlight.rect)

    def fillAll(self, color):
        for y in range(16):
            for x in range(16):
                self.colorPixel((x,y), color)

    def execute(self):
        self.setup()
        while not self.complete:

            if self.saveActive:

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.complete = True

                    if event.type == pygame.KEYDOWN:

                        key = chr(event.key)

                        if event.key == pygame.K_s and pygame.key.get_mods() & pygame.KMOD_SHIFT:
                            if self.saveName is not '':
                                pygame.image.save(self.canvas, "{}.png".format(self.saveName))
                            self.saveNameDelete(True)
                            self.saveActive = False

                        else:

                            if key in PixelDraw.FILENAME_SET:
                                self.saveNameAdd(key)
                            elif event.key == pygame.K_BACKSPACE:
                                print("DELETE")
                                self.saveNameDelete(False)



            else:

                moved = False

                for event in pygame.event.get():
                    if event.type == pygame.QUIT:
                        self.complete = True

                    if event.type == pygame.KEYDOWN:

                        if event.key == pygame.K_RIGHT:
                            moved = True
                            self.setCanvasPointer((self.canvasPointer[0] + 1, self.canvasPointer[1]))
                        if event.key == pygame.K_LEFT:
                            moved = True
                            self.setCanvasPointer((self.canvasPointer[0] - 1, self.canvasPointer[1]))
                        if event.key == pygame.K_UP:
                            moved = True
                            self.setCanvasPointer((self.canvasPointer[0], self.canvasPointer[1] - 1))
                        if event.key == pygame.K_DOWN:
                            moved = True
                            self.setCanvasPointer((self.canvasPointer[0], self.canvasPointer[1] + 1))

                        if event.key == pygame.K_x:
                            self.fillAll(self.transparentColor)

                        if event.key == pygame.K_c:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                self.copyColor(self.canvasPointer)

                        if event.key == pygame.K_v:
                            color = self.COLORS[self.categoryPointer][self.colorPointer]
                            self.bucketFill(self.canvasPointer, color)

                        if event.key == pygame.K_t:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                self.setSpecialColor(0, self.pixelGrid[self.canvasPointer[1]][self.canvasPointer[0]])
                            elif pygame.key.get_mods() & pygame.KMOD_ALT:
                                self.setSpecialColor(0, self.COLORS[self.categoryPointer][self.colorPointer])
                            else:
                                self.colorPixel(self.canvasPointer, self.transparentColor)

                        if event.key == pygame.K_b:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                self.setSpecialColor(1, self.pixelGrid[self.canvasPointer[1]][self.canvasPointer[0]])
                            elif pygame.key.get_mods() & pygame.KMOD_ALT:
                                self.setSpecialColor(1, self.COLORS[self.categoryPointer][self.colorPointer])
                            else:
                                self.colorPixel(self.canvasPointer, self.backdropColor)

                        if event.key == pygame.K_m:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                self.setSpecialColor(2, self.pixelGrid[self.canvasPointer[1]][self.canvasPointer[0]])
                            elif pygame.key.get_mods() & pygame.KMOD_ALT:
                                self.setSpecialColor(2, self.COLORS[self.categoryPointer][self.colorPointer])
                            else:
                                self.colorPixel(self.canvasPointer, self.memoryColor)

                        if event.key == pygame.K_LEFTBRACKET:
                            self.setCategoryPointer(self.NEXT_CATEGORY_LEFT[self.categoryPointer])

                        if event.key == pygame.K_RIGHTBRACKET:
                            self.setCategoryPointer(self.NEXT_CATEGORY_RIGHT[self.categoryPointer])

                        if event.key == pygame.K_s:
                            if pygame.key.get_mods() & pygame.KMOD_SHIFT:
                                self.saveActive = True
                                #pygame.image.save(self.canvas, "saved.png")

                        if event.key == pygame.K_g:
                            self.useGrid = not self.useGrid

                        if event.key in PixelDraw.NUMBERS:
                            self.setColorPointer(event.key - 48, False)

                if moved:
                    self.elapsedTime['move'] = 0

                pressedKeys = pygame.key.get_pressed()

                if pressedKeys[pygame.K_RIGHT]:
                    if self.elapsedTime['move'] >= PixelDraw.TIMES['move']:
                        self.setCanvasPointer((self.canvasPointer[0] + 1, self.canvasPointer[1]))
                if pressedKeys[pygame.K_LEFT]:
                    if self.elapsedTime['move'] >= PixelDraw.TIMES['move']:
                        self.setCanvasPointer((self.canvasPointer[0] - 1, self.canvasPointer[1]))
                if pressedKeys[pygame.K_UP]:
                    if self.elapsedTime['move'] >= PixelDraw.TIMES['move']:
                        self.setCanvasPointer((self.canvasPointer[0], self.canvasPointer[1] - 1))
                if pressedKeys[pygame.K_DOWN]:
                    if self.elapsedTime['move'] >= PixelDraw.TIMES['move']:
                        self.setCanvasPointer((self.canvasPointer[0], self.canvasPointer[1] + 1))
                if pressedKeys[pygame.K_SPACE]:
                    color = self.COLORS[self.categoryPointer][self.colorPointer]
                    colored = self.colorPixel(self.canvasPointer, color)
                    if colored:
                        self.historyState()

                if pressedKeys[pygame.K_q]:
                    if self.elapsedTime['undo'] >= PixelDraw.TIMES['undo']:
                        self.undo()
                        self.elapsedTime['undo'] = 0

                if pressedKeys[pygame.K_w]:
                    if self.elapsedTime['undo'] >= PixelDraw.TIMES['undo']:
                        self.redo()
                        self.elapsedTime['undo'] = 0

                if pressedKeys[pygame.K_d]:
                    if self.colorPointer != 0 and self.elapsedTime['cp'] >= PixelDraw.TIMES['cp']:
                        self.setColorPointer(self.colorPointer - 1, True)
                        self.elapsedTime['cp'] = 0

                if pressedKeys[pygame.K_f]:
                    if self.colorPointer != 9 and self.elapsedTime['cp'] >= PixelDraw.TIMES['cp']:
                        self.setColorPointer(self.colorPointer + 1, True)
                        self.elapsedTime['cp'] = 0


            self.screen.fill(BLACK)
            self.screen.blit(self.background, self.backgroundRect)
            self.drawSprites()
            if self.useGrid:
                self.screen.blit(self.grid, self.gridRect)
            if self.saveActive:
                self.screen.blit(self.saveDialogBackground, self.saveDialogRect)
                self.screen.blit(self.saveNameSurface, (self.SAVECOORDINATES['name'][0],self.SAVECOORDINATES['name'][1]))
                self.screen.blit(self.saveTransparencyColorBox.image, self.saveTransparencyColorBox.rect)

            delta = self.clock.tick(60)
            for k in self.elapsedTime:
                if self.elapsedTime[k] < 1000:
                    self.elapsedTime[k] += delta
            pygame.display.flip()

        pygame.quit()

    def historyState(self):
        self.history.pushState([x[:] for x in self.pixelGrid], self.historyPointer)
        self.historyPointer = 0

    def newCanvas(self):
        self.canvases += 1
        self.canvas = pygame.Surface((16,16))
        self.canvasRectangle = self.canvas.get_rect()

        for y in range(16):
            for x in range(16):
                p = Pixel()
                p.rect.x = self.COORDINATES['canvas'][0] + (32 * x)
                p.rect.y = self.COORDINATES['canvas'][1] + (32 * y)
                self.canvasSprites[y][x] = p
                self.pixelGrid[y][x] = (0, 0, 0)
                self.canvasList.add(p)

        self.setCanvas(self.canvases - 1)

    def saveNameAdd(self, character):
        position = len(self.saveName)
        if position < 16:
            self.saveName += character
            enlargedText = pygame.transform.scale(self.FONT[character.upper()], (16, 16))
            self.saveNameSurface.blit(enlargedText,(16*position,0))

    def saveNameDelete(self, all):
        position = len(self.saveName)
        if position > 0 and all:
            self.saveName = ""
            self.saveNameSurface.fill(BLACK)
            for i, c in enumerate(['.', 'P', 'N', 'G']):
                enlargedText = pygame.transform.scale(self.FONT[c], (16, 16))
                self.saveNameSurface.blit(enlargedText, (16 * (16 + i), 0))
            arr = pygame.PixelArray(self.saveNameSurface)
            arr.replace(WHITE, COMMODORE)
            del arr
        elif position > 0:
            blackText = pygame.Surface((16,16))
            blackText.fill(BLACK)
            self.saveName = self.saveName[:-1]
            print(self.saveName)
            self.saveNameSurface.blit(blackText, (16 * (position-1), 0))



    def setCanvas(self, num):
        self.currentCanvas = num
        # TODO multiple canvas support for animation testing
        self.canvasRectangle.x = self.COORDINATES['size16'][0]
        self.canvasRectangle.y = self.COORDINATES['size16'][1]
        self.previewList.update(self.canvas)

    def setCategoryPointer(self, colorGroup):
        self.categoryPointer = colorGroup
        for i in range(10):
            self.colorSprites[i].update(tuple(self.COLORS[self.categoryPointer][i]))

    def setColorPointer(self, num, move):
        if 0 <= num < 10:
            if not move:
                if num == 0:
                    num = 9
                else:
                    num -= 1
            self.colorPointer = num
            self.colorHighlight.update(self.COORDINATES['colorHighlight'][0] + (num * 37), self.COORDINATES['colorHighlight'][1])

    def setCanvasPointer(self, coordinate):
        if 0 <= coordinate[0] < 16 and 0 <= coordinate[1] < 16:
            self.canvasPointer = coordinate
            newX = self.COORDINATES['canvas'][0] + (self.canvasPointer[0] * 32)
            newY = self.COORDINATES['canvas'][1] + (self.canvasPointer[1] * 32)
            self.canvasHighlight.update(newX, newY)

    def setSpecialColor(self, colorType, color):
        # 0 = transparency
        # 1 = backdrop
        # 2 = memory
        if colorType == 0:
            self.transparentColor = color
            self.saveTransparencyColorBox.update(color)
        elif colorType == 1:
            self.backdropColor = color
        elif colorType == 2:
            self.memoryColor = color

        self.specialColorSprites[colorType].update(color)

    def redo(self):
        if self.historyPointer > 0:
            self.historyPointer -= 1
            grid = self.history.get(self.historyPointer)
            self.pixelGrid = [x[:] for x in grid]
            self.applyPixelGrid(grid)
        else:
            print("Cannot Redo")
            #print(self.historyPointer)

    def undo(self):
        if self.historyPointer + 1 < len(self.history.states):
            self.historyPointer += 1
            grid = self.history.get(self.historyPointer)
            self.pixelGrid = [x[:] for x in grid]
            self.applyPixelGrid(grid)
        else:
            print("Cannot Undo")
            #print(self.historyPointer)

if __name__ == '__main__':
    pd = PixelDraw()
    pd.execute()