import pygame
from pd_parse import parse
from pd_objects import Canvas, Element, History, TextBox

class PixelDraw:

    TIMES = {
        'move': 200,
        'undo': 100,
        'cp': 150
    }

    BLK = (0, 0, 0)
    WHT = (255, 255, 255)
    RED = (255, 0, 0)
    BLU = (0, 0, 255)
    GRN = (0, 255, 0)
    AQA = (0, 255, 255)
    PRP = (255, 0, 255)
    YLW = (255, 255, 0)
    COM = (158, 150, 242)

    RANGE_VALUES = {
        'labelNumbers' : ('1','2','3','4','5','6','7','8','9','0'),
        'labelSpecials' : ('T','B','M')
    }

    NEXT_CATEGORY_RIGHT = {
        'white': 'red',
        'red': 'orange',
        'orange': 'green',
        'green': 'blue',
        'blue': 'purple',
        'purple': 'white'
    }

    NEXT_CATEGORY_LEFT = {
        'white': 'purple',
        'red': 'white',
        'orange': 'red',
        'green': 'orange',
        'blue': 'green',
        'purple': 'blue'
    }

    CATEGORY_LABELS = {
        'white' : 'labelWhite',
        'red' : 'labelRed',
        'orange' : 'labelOrange',
        'green' : 'labelGreen',
        'blue' : 'labelBlue',
        'purple': 'labelPurple'
    }

    def __init__(self, screen, x, y):
        # General
        self.x = x
        self.y = y
        self.screen = screen
        self.clock = pygame.time.Clock()
        self.complete = False
        self.histories = [History()]
        self.elapsedTime = dict(PixelDraw.TIMES)
        self.useGrid = False

        # Navigation
        self.directory = 'main'            # Which Menu Are We In
        self.historyPointer = 0
        self.categoryPointer = None  # which color type
        self.colorPointer = 0  # which color
        self.canvasPointer = None  # where on the canvas

        # Data
        self.canvases = [Canvas()]
        self.currentCanvas = self.canvases[0]
        self.transparentColor = PixelDraw.BLK
        self.backdropColor = PixelDraw.BLK
        self.memoryColor = PixelDraw.BLK

        # ELEMENTS

        self.ele = {}               # MenuName : ElementName : Element
        self.men = {}               # MenuName : [x,y,parent]
        self.col = {}               # Category : [color, color, ...]
        self.off = {}               # ElementName : (x,y)
        self.grp = {}               # GroupName : group


        self.parseDataFiles(['colors2.txt','elements.txt'])
        self.setCategoryPointer('white')
        self.setCanvasPointer((0,0))
        self.setColorPointer(0)

    def createElement(self, data, menuName):
        outputElements = []
        elementClass = data['class']
        elementName = data['name']
        numberOfElements = (1,1)                    # x * y = number of elements
        offset = (0,0)
        if 'offset' in data:
            offset = eval(data['offset'])
            self.off[menuName][elementName] = offset
        elementGroup = None
        if 'group' in data:
            elementGroup = data['group']
        if elementClass == 'array':
            numberOfElements = eval(data['extent'])

        elementType = data['type']
        elementLocation = eval(data['location'])

        if elementType == 'label':
            #fontColor = PixelDraw.WHT
            fontSize = int(data['font'])
            if 'text_color' in data:
                #fontColor = data['text_color']
                pass
            if 'text' in data:
                text = data['text'].replace('_',' ').upper()
                e = TextBox.fromText(text, fontSize, elementLocation[0], elementLocation[1])
            else:
                e = TextBox(16, 1, 16, elementLocation[0], elementLocation[1])
            outputElements.append(e)
        else:
            if 'size' in data:
                elementSize = eval(data['size'])
                for y in range(numberOfElements[1]):
                    outputElements.append([])
                    for x in range(numberOfElements[0]):
                        e = Element(elementSize[0], elementSize[1],
                                    elementLocation[0]+(offset[0]*x), elementLocation[1]+(offset[1]*y),
                                    elementType)
                        if elementGroup is not None:
                            if elementGroup not in self.grp:
                                self.grp[elementGroup] = pygame.sprite.Group()
                            self.grp[elementGroup].add(e)
                        outputElements[y].append(e)
            else:
                imageFile = data['image']
                e = Element.fromFile(imageFile, elementLocation[0], elementLocation[1], elementType)
                if elementGroup is not None:
                    if elementGroup not in self.grp:
                        self.grp[elementGroup] = pygame.sprite.Group()
                    self.grp[elementGroup].add(e)
                outputElements.append(e)

        if elementClass != 'array':
            while type(outputElements) == list:
                outputElements = outputElements[0]
        else:
            if type(outputElements) == list and len(outputElements) == 1:
                outputElements = outputElements[0]
            newOut = []
            for sub in outputElements:
                if type(sub) == list and len(sub) == 1:
                    newOut.append(sub[0])
                else:
                    newOut.append(sub)
            outputElements = newOut
        #print(data['name'])
        #print(outputElements)
        #print()
        #print(outputElements)
        return outputElements

    def parseDataFiles(self, fileList):
        for file in fileList:
            data, filetype = parse(file)

            if filetype == 'colors':
                for menu in data:
                    if menu['class'] == 'category':
                        self.col[menu['name']] = []
                    for color in menu['elements']:
                        self.col[menu['name']].append(eval(color['rgb']))

            elif filetype == 'elements':
                for menu in data:
                    menuName = menu['name']
                    try:
                        menuLocation = eval(menu['location'])
                        menuX = menuLocation[0]
                        menuY = menuLocation[1]
                        menuParent = menu['parent']
                    except:
                        menuX = 0
                        menuY = 0
                        menuParent = None
                    self.men[menuName] = (menuX, menuY, menuParent)
                    self.ele[menuName] = {}
                    self.off[menuName] = {}
                    for element in menu['elements']:
                        if 'name' in element and element['class'] not in ('range', 'burn'):     # Random Access Element
                            elementName = element['name']
                            self.ele[menuName][elementName] = self.createElement(element, menuName)
                        elif element['class'] in ('range', 'burn'):                                  # blit / burn text
                            elementClass = element['class']
                            if 'type' in element:
                                elementType = element['type']
                            else:
                                elementType = 'burn'
                            elementOnto = element['onto']
                            elementFont = int(element['font'])
                            elementLocation = eval(element['location'])
                            offset = (0, 0)
                            if elementClass == 'range':
                                numberOfElements = eval(element['extent'])
                                offset = eval(element['offset'])
                                values = PixelDraw.RANGE_VALUES[element['name']]
                                i = 0
                                for y in range(numberOfElements[1]):
                                    for x in range(numberOfElements[0]):
                                        TextBox.burnText(self.ele[menuName][elementOnto].image, values[i], elementFont,
                                                         elementLocation[0] + (x * offset[0]),
                                                         elementLocation[1] + (y * offset[1]))
                                        i += 1
                            else:
                                text = element['text'].upper().replace('_', ' ')
                                TextBox.burnText(self.ele[menuName][elementOnto].image, text, elementFont,
                                                 elementLocation[0],elementLocation[1])


    #################################################################################################

    def newCanvas(self):
        return None

    def setCanvasPointer(self, coordinates):
        self.canvasPointer = coordinates
        trueCoordinates = (10+(32*coordinates[0]),10+(32*coordinates[1]))
        self.ele['main']['highlightCanvas'].update(trueCoordinates)

    def setCategoryPointer(self, category):
        self.categoryPointer = category
        for i in range(10):
            self.ele['main']['colorPalette'][i].fill(self.col[self.categoryPointer][i])

    def setColorPointer(self, num):
        self.colorPointer = num


    #################################################################################################

    def drawElement(self, element, location=None):
        if location is None:
            location = element.rect
        self.screen.blit(element.image, location)

    def drawScreen(self):
        self.screen.fill(PixelDraw.BLK)
        self.screen.blit(self.ele['main']['background'].image, self.ele['main']['background'].rect)

        if self.directory == 'main':
            self.grp['colorPalette'].draw(self.screen) # TODO
            categoryLabel = PixelDraw.CATEGORY_LABELS[self.categoryPointer]
            self.drawElement(self.ele['main'][categoryLabel])
            #print(self.ele)
            #print(self.ele['main']['colorPalette'])
            #self.drawElement(self.ele['main']['colorPalette'][1])
            self.grp['highlights'].draw(self.screen)
        pygame.display.flip()

    def execute(self):

        while not self.complete:

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    self.complete = True


            self.drawScreen()
            self.clock.tick(60)

        pygame.quit()

if __name__ == '__main__':
    pygame.init()
    screen = pygame.display.set_mode((800, 640))
    pd = PixelDraw(screen, 800, 640)
    pd.execute()