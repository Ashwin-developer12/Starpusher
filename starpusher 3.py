import random, sys, copy, os, pygame
from pygame.locals import *

fps = 30 
winwidth = 800 
winheight = 600 
half_winwidth = int(winwidth / 2)
half_winheight = int(winheight / 2)

tilewidth = 50
tileheight = 85
tilefloorheight = 40

CAM_MOVE_SPEED = 5

outside_decoration_pct = 20

brightblue = (  0, 170, 255)
white      = (255, 255, 255)
bgcolour = brightblue
textcolour = white

UP = 'up'
DOWN = 'down'
LEFT = 'left'
RIGHT = 'right'


def main():
    global fpsclock, displaysurf, imagesdict, tilemapping, outsidedecomapping, basicfont, playerimages, currentimage

    pygame.init()
    fpsclock = pygame.time.Clock()

    displaysurf = pygame.display.set_mode((winwidth, winheight))

    pygame.display.set_caption('Star Pusher')
    basicfont = pygame.font.Font('freesansbold.ttf', 18)

    imagesdict = {'uncovered goal': pygame.image.load('RedSelector.png'),
                  'covered goal': pygame.image.load('Selector.png'),
                  'star': pygame.image.load('Star.png'),
                  'corner': pygame.image.load('Wall_Block_Tall.png'),
                  'wall': pygame.image.load('Wood_Block_Tall.png'),
                  'inside floor': pygame.image.load('Plain_Block.png'),
                  'outside floor': pygame.image.load('Grass_Block.png'),
                  'title': pygame.image.load('star_title.png'),
                  'solved': pygame.image.load('star_solved.png'),
                  'princess': pygame.image.load('princess.png'),
                  'boy': pygame.image.load('boy.png'),
                  'catgirl': pygame.image.load('catgirl.png'),
                  'horngirl': pygame.image.load('horngirl.png'),
                  'pinkgirl': pygame.image.load('pinkgirl.png'),
                  'rock': pygame.image.load('Rock.png'),
                  'short tree': pygame.image.load('Tree_Short.png'),
                  'tall tree': pygame.image.load('Tree_Tall.png'),
                  'ugly tree': pygame.image.load('Tree_Ugly.png')}

    tilemapping = {'x': imagesdict['corner'],
                   '#': imagesdict['wall'],
                   'o': imagesdict['inside floor'],
                   ' ': imagesdict['outside floor']}
    outsidedecomapping = {'1': imagesdict['rock'],
                          '2': imagesdict['short tree'],
                          '3': imagesdict['tall tree'],
                          '4': imagesdict['ugly tree']}

    currentimage = 0
    playerimages = [imagesdict['princess'],
                    imagesdict['boy'],
                    imagesdict['catgirl'],
                    imagesdict['horngirl'],
                    imagesdict['pinkgirl']]

    startscreen() 
    levels = readLevelsFile('starPusherLevels.txt')
    currentLevelIndex = 0

    while True:
        result = runLevel(levels, currentLevelIndex)

        if result in ('solved', 'next'):
            currentLevelIndex += 1
            if currentLevelIndex >= len(levels):
                currentLevelIndex = 0
        elif result == 'back':
            currentLevelIndex -= 1
            if currentLevelIndex < 0:
                currentLevelIndex = len(levels)-1
        elif result == 'reset':
            pass 


def runLevel(levels, levelNum):
    global currentimage
    levelObj = levels[levelNum]
    mapobj = decorateMap(levelObj['mapobj'], levelObj['startState']['player'])
    gameStateObj = copy.deepcopy(levelObj['startState'])
    mapNeedsRedraw = True 
    levelSurf = basicfont.render('Level %s of %s' % (levelNum + 1, len(levels)), 1, textcolour)
    levelRect = levelSurf.get_rect()
    levelRect.bottomleft = (20, winheight - 35)
    mapWidth = len(mapobj) * tilewidth
    mapHeight = (len(mapobj[0]) - 1) * tilefloorheight + tileheight
    MAX_CAM_X_PAN = abs(half_winheight - int(mapHeight / 2)) + tilewidth
    MAX_CAM_Y_PAN = abs(half_winwidth - int(mapWidth / 2)) + tileheight

    levelIsComplete = False
    cameraOffsetX = 0
    cameraOffsetY = 0
    cameraUp = False
    cameraDown = False
    cameraLeft = False
    cameraRight = False

    while True: 
        playerMoveTo = None
        keyPressed = False

        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()

            elif event.type == KEYDOWN:
                keyPressed = True
                if event.key == K_LEFT:
                    playerMoveTo = LEFT
                elif event.key == K_RIGHT:
                    playerMoveTo = RIGHT
                elif event.key == K_UP:
                    playerMoveTo = UP
                elif event.key == K_DOWN:
                    playerMoveTo = DOWN

                elif event.key == K_a:
                    cameraLeft = True
                elif event.key == K_d:
                    cameraRight = True
                elif event.key == K_w:
                    cameraUp = True
                elif event.key == K_s:
                    cameraDown = True

                elif event.key == K_n:
                    return 'next'
                elif event.key == K_b:
                    return 'back'

                elif event.key == K_ESCAPE:
                    terminate()
                elif event.key == K_BACKSPACE:
                    return 'reset'
                elif event.key == K_p:
                    currentimage += 1
                    if currentimage >= len(playerimages):
                        currentimage = 0
                    mapNeedsRedraw = True

            elif event.type == KEYUP:
                if event.key == K_a:
                    cameraLeft = False
                elif event.key == K_d:
                    cameraRight = False
                elif event.key == K_w:
                    cameraUp = False
                elif event.key == K_s:
                    cameraDown = False

        if playerMoveTo != None and not levelIsComplete:
            moved = makeMove(mapobj, gameStateObj, playerMoveTo)

            if moved:
                gameStateObj['stepCounter'] += 1
                mapNeedsRedraw = True

            if isLevelFinished(levelObj, gameStateObj):
                levelIsComplete = True
                keyPressed = False

        displaysurf.fill(bgcolour)

        if mapNeedsRedraw:
            mapSurf = drawMap(mapobj, gameStateObj, levelObj['goals'])
            mapNeedsRedraw = False

        if cameraUp and cameraOffsetY < MAX_CAM_X_PAN:
            cameraOffsetY += CAM_MOVE_SPEED
        elif cameraDown and cameraOffsetY > -MAX_CAM_X_PAN:
            cameraOffsetY -= CAM_MOVE_SPEED
        if cameraLeft and cameraOffsetX < MAX_CAM_Y_PAN:
            cameraOffsetX += CAM_MOVE_SPEED
        elif cameraRight and cameraOffsetX > -MAX_CAM_Y_PAN:
            cameraOffsetX -= CAM_MOVE_SPEED

        mapSurfRect = mapSurf.get_rect()
        mapSurfRect.center = (half_winwidth + cameraOffsetX, half_winheight + cameraOffsetY)

        displaysurf.blit(mapSurf, mapSurfRect)

        displaysurf.blit(levelSurf, levelRect)
        stepSurf = basicfont.render('Steps: %s' % (gameStateObj['stepCounter']), 1, textcolour)
        stepRect = stepSurf.get_rect()
        stepRect.bottomleft = (20, winheight - 10)
        displaysurf.blit(stepSurf, stepRect)

        if levelIsComplete:
            solvedRect = imagesdict['solved'].get_rect()
            solvedRect.center = (half_winwidth, half_winheight)
            displaysurf.blit(imagesdict['solved'], solvedRect)

            if keyPressed:
                return 'solved'

        pygame.display.update()
        fpsclock.tick()


def isWall(mapobj, x, y):
    
    if x < 0 or x >= len(mapobj) or y < 0 or y >= len(mapobj[x]):
        return False 
    elif mapobj[x][y] in ('#', 'x'):
        return True 
    return False


def decorateMap(mapobj, startxy):
    

    startx, starty = startxy

    mapobjCopy = copy.deepcopy(mapobj)

    for x in range(len(mapobjCopy)):
        for y in range(len(mapobjCopy[0])):
            if mapobjCopy[x][y] in ('$', '.', '@', '+', '*'):
                mapobjCopy[x][y] = ' '

    floodFill(mapobjCopy, startx, starty, ' ', 'o')

    for x in range(len(mapobjCopy)):
        for y in range(len(mapobjCopy[0])):

            if mapobjCopy[x][y] == '#':
                if (isWall(mapobjCopy, x, y-1) and isWall(mapobjCopy, x+1, y)) or \
                   (isWall(mapobjCopy, x+1, y) and isWall(mapobjCopy, x, y+1)) or \
                   (isWall(mapobjCopy, x, y+1) and isWall(mapobjCopy, x-1, y)) or \
                   (isWall(mapobjCopy, x-1, y) and isWall(mapobjCopy, x, y-1)):
                    mapobjCopy[x][y] = 'x'

            elif mapobjCopy[x][y] == ' ' and random.randint(0, 99) < outside_decoration_pct:
                mapobjCopy[x][y] = random.choice(list(outsidedecomapping.keys()))

    return mapobjCopy


def isBlocked(mapobj, gameStateObj, x, y):
   
    if isWall(mapobj, x, y):
        return True

    elif x < 0 or x >= len(mapobj) or y < 0 or y >= len(mapobj[x]):
        return True 

    elif (x, y) in gameStateObj['stars']:
        return True 

    return False


def makeMove(mapobj, gameStateObj, playerMoveTo):
    

    playerx, playery = gameStateObj['player']

    stars = gameStateObj['stars']

    if playerMoveTo == UP:
        xoffset = 0
        yOffset = -1
    elif playerMoveTo == RIGHT:
        xoffset = 1
        yOffset = 0
    elif playerMoveTo == DOWN:
        xoffset = 0
        yOffset = 1
    elif playerMoveTo == LEFT:
        xoffset = -1
        yOffset = 0

    if isWall(mapobj, playerx + xoffset, playery + yOffset):
        return False
    else:
        if (playerx + xoffset, playery + yOffset) in stars:
            if not isBlocked(mapobj, gameStateObj, playerx + (xoffset*2), playery + (yOffset*2)):
                ind = stars.index((playerx + xoffset, playery + yOffset))
                stars[ind] = (stars[ind][0] + xoffset, stars[ind][1] + yOffset)
            else:
                return False
        gameStateObj['player'] = (playerx + xoffset, playery + yOffset)
        return True


def startscreen():
    

    titleRect = imagesdict['title'].get_rect()
    topCoord = 50 
    titleRect.top = topCoord
    titleRect.centerx = half_winwidth
    topCoord += titleRect.height

    inst_text = ['Push the stars over the marks.',
                       'Arrow keys to move',
                       ' Esc to quit.']

    displaysurf.fill(bgcolour)

    displaysurf.blit(imagesdict['title'], titleRect)

    for i in range(len(inst_text)):
        instsurf = basicfont.render(inst_text[i], 1, textcolour)
        instrect = instsurf.get_rect()
        topCoord += 10 
        instrect.top = topCoord
        instrect.centerx = half_winwidth
        topCoord += instrect.height 
        displaysurf.blit(instsurf, instrect)

    while True:
        for event in pygame.event.get():
            if event.type == QUIT:
                terminate()
            elif event.type == KEYDOWN:
                if event.key == K_ESCAPE:
                    terminate()
                return

        pygame.display.update()
        fpsclock.tick()


def readLevelsFile(filename):
    assert os.path.exists(filename), 'Cannot find the level file: %s' % (filename)
    mapfile = open(filename, 'r')
    content = mapfile.readlines() + ['\r\n']
    mapfile.close()

    levels = [] 
    levelNum = 0
    maptextlines = []
    mapobj = []
    for lineNum in range(len(content)):
        line = content[lineNum].rstrip('\r\n')

        if ';' in line:
            line = line[:line.find(';')]

        if line != '':
            maptextlines.append(line)
        elif line == '' and len(maptextlines) > 0:
            maxWidth = -1
            for i in range(len(maptextlines)):
                if len(maptextlines[i]) > maxWidth:
                    maxWidth = len(maptextlines[i])
            for i in range(len(maptextlines)):
                maptextlines[i] += ' ' * (maxWidth - len(maptextlines[i]))

            for x in range(len(maptextlines[0])):
                mapobj.append([])
            for y in range(len(maptextlines)):
                for x in range(maxWidth):
                    mapobj[x].append(maptextlines[y][x])

            startx = None
            starty = None
            goals = []
            stars = []
            for x in range(maxWidth):
                for y in range(len(mapobj[x])):
                    if mapobj[x][y] in ('@', '+'):
                        startx = x
                        starty = y
                    if mapobj[x][y] in ('.', '+', '*'):
                        goals.append((x, y))
                    if mapobj[x][y] in ('$', '*'):
                        stars.append((x, y))

            assert startx != None and starty != None, 'Level %s (around line %s) in %s is missing a "@" or "+" to mark the start point.' % (levelNum+1, lineNum, filename)
            assert len(goals) > 0, 'Level %s (around line %s) in %s must have at least one goal.' % (levelNum+1, lineNum, filename)
            assert len(stars) >= len(goals), 'Level %s (around line %s) in %s is impossible to solve. It has %s goals but only %s stars.' % (levelNum+1, lineNum, filename, len(goals), len(stars))

            gameStateObj = {'player': (startx, starty),
                            'stepCounter': 0,
                            'stars': stars}
            levelObj = {'width': maxWidth,
                        'height': len(mapobj),
                        'mapobj': mapobj,
                        'goals': goals,
                        'startState': gameStateObj}

            levels.append(levelObj)

            maptextlines = []
            mapobj = []
            gameStateObj = {}
            levelNum += 1
    return levels


def floodFill(mapobj, x, y, oldCharacter, newCharacter):
    
    if mapobj[x][y] == oldCharacter:
        mapobj[x][y] = newCharacter

    if x < len(mapobj) - 1 and mapobj[x+1][y] == oldCharacter:
        floodFill(mapobj, x+1, y, oldCharacter, newCharacter)
    if x > 0 and mapobj[x-1][y] == oldCharacter:
        floodFill(mapobj, x-1, y, oldCharacter, newCharacter)
    if y < len(mapobj[x]) - 1 and mapobj[x][y+1] == oldCharacter:
        floodFill(mapobj, x, y+1, oldCharacter, newCharacter)
    if y > 0 and mapobj[x][y-1] == oldCharacter:
        floodFill(mapobj, x, y-1, oldCharacter, newCharacter)


def drawMap(mapobj, gameStateObj, goals):
    

    mapSurfWidth = len(mapobj) * tilewidth
    mapSurfHeight = (len(mapobj[0]) - 1) * tilefloorheight + tileheight
    mapSurf = pygame.Surface((mapSurfWidth, mapSurfHeight))
    mapSurf.fill(bgcolour)

    for x in range(len(mapobj)):
        for y in range(len(mapobj[x])):
            spacerect = pygame.Rect((x * tilewidth, y * tilefloorheight, tilewidth, tileheight))
            if mapobj[x][y] in tilemapping:
                baseTile = tilemapping[mapobj[x][y]]
            elif mapobj[x][y] in outsidedecomapping:
                baseTile = tilemapping[' ']

            mapSurf.blit(baseTile, spacerect)

            if mapobj[x][y] in outsidedecomapping:
                mapSurf.blit(outsidedecomapping[mapobj[x][y]], spacerect)
            elif (x, y) in gameStateObj['stars']:
                if (x, y) in goals:
                    mapSurf.blit(imagesdict['covered goal'], spacerect)
                mapSurf.blit(imagesdict['star'], spacerect)
            elif (x, y) in goals:
                mapSurf.blit(imagesdict['uncovered goal'], spacerect)

            if (x, y) == gameStateObj['player']:
                mapSurf.blit(playerimages[currentimage], spacerect)

    return mapSurf


def isLevelFinished(levelObj, gameStateObj):
        for goal in levelObj['goals']:
            if goal not in gameStateObj['stars']:
                return False
        return True


def terminate():
    pygame.quit()
    sys.exit()


if __name__ == '__main__':
    main()
