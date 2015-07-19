from random import choice, randint
import pygame, sys
from pygame.locals import *
from copy import deepcopy

FPS = 30 # frames per second, the general speed of the program
WINDOWWIDTH = 650 # size of window's width in pixels
WINDOWHEIGHT = 600 # size of windows' height in pixels
REVEALSPEED = 12 # speed boxes' sliding reveals and covers
BOXSIZE = 90 # size of box height & width in pixels
GAPSIZE = 15 # size of gap between boxes in pixels

BASICFONTSIZE = 40

XMARGIN = int((WINDOWWIDTH - (4* (BOXSIZE + GAPSIZE))) / 2)
YMARGIN = int((WINDOWHEIGHT - (4 * (BOXSIZE + GAPSIZE))) / 2)

#            R    G    B
BGCOLOR =  (180, 180, 180)
BOXCOLOR = (110, 110, 110)
TXT1    =  (120, 120, 120)# 2, 4
TXT2    =  (255, 255, 255)# 8 and up
c2       = (250, 245, 245)
c4       = (237, 232, 211)
c8       = (247, 194, 136)
c16      = (250, 173, 125)
c32      = (250, 135, 90)
c64      = ( 250, 50, 50)
c128     = (  238, 242, 121)
c256     = (245, 233, 103)
c512     = (247, 216, 77)
c1024    = (252, 204, 45)
c2048   =  (  192, 192, 254)

colorDict = {0: BOXCOLOR, 2 : c2, 4 : c4, 8 : c8, 16: c16, 32: c32,
             64: c64, 128:c128, 256 : c256, 512:c512, 1024:c1024, 2048:c2048}

##moveAnimation(board, target, number, direction)
#make hasSpace()

#animations are gonna be the hard part.
#need to redo slide funcs to incorporate animation
def main():
    global FPSCLOCK, DISPLAYSURF, BASICFONT, BIGFONT
    pygame.init()
    FPSCLOCK = pygame.time.Clock()
    DISPLAYSURF = pygame.display.set_mode((WINDOWWIDTH, WINDOWHEIGHT))
    BASICFONT = pygame.font.Font('freesansbold.ttf', BASICFONTSIZE)
    BIGFONT = pygame.font.Font('freesansbold.ttf', int(BASICFONTSIZE * 1.333))
    newBox = False
    
    while True:
        gameBoard = [[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0],[0, 0, 0, 0]]
        drawBoxes(gameBoard)
        addNew(gameBoard)
        addNew(gameBoard)
        drawBoxes(gameBoard)
        while True: # main game loop
            
            if not hasSpaceLeft(gameBoard):
                if checkLost(gameBoard):
                    loseAnimation()
                    break
            
            for event in pygame.event.get(): # event handling loop
                if event.type == QUIT or (event.type == KEYUP and event.key == K_ESCAPE):
                    pygame.quit()
                    sys.exit()
                elif event.type == KEYUP:
                    if event.key in (K_LEFT, K_a):
                        newBox = slideLeft(gameBoard)
                    elif event.key in (K_RIGHT, K_d):
                        newBox =  slideRight(gameBoard)
                    elif event.key in (K_UP, K_w):
                        newBox = slideUp(gameBoard)
                    elif event.key in (K_DOWN, K_s):
                        newBox = slideDown(gameBoard)
                    drawBoxes(gameBoard)
                    if newBox:
                        addNew(gameBoard)
                        drawBoxes(gameBoard)
                        newBox = False
            

def shiftBoxes(boxes, shiftedBoxes, direction):
    #targets is 4x4 list with 'true' for boxes that will be moved
    incr = int((BOXSIZE + GAPSIZE) / 2)
    shiftx = 0
    shifty = 0
    if direction== "down":
        shifty = incr
    elif direction == "up":
        shifty = -incr
    elif direction == "left":
        shiftx = -incr
    elif direction == "right":
        shiftx = incr

    for x in range(2):
        drawBoxes(boxes, shiftedBoxes, shifty * x, shiftx * x)

              
def drawBoxes(boxes, shiftedBoxes = [], shifty = 0, shiftx = 0):
    #draw all board, some boxes shifted (for animation)
    if shiftedBoxes == []:
        shiftedBoxes = [[0, 0, 0, 0], [0, 0, 0, 0], [0, 0, 0, 0],[0, 0, 0, 0]]
        
    DISPLAYSURF.fill(BGCOLOR)
    for y in range(4):
        for x in range(4):
            left, top = leftTopCoordsOfBox(x, y)
            pygame.draw.rect(DISPLAYSURF, BOXCOLOR, (left-2, top-2, BOXSIZE+4, BOXSIZE+4)) #bkground box
            if shiftedBoxes[y][x] == 0: #display box in normal spot
                val = boxes[y][x]
                    
                pygame.draw.rect(DISPLAYSURF, colorDict[val], (left, top, BOXSIZE, BOXSIZE))
                if val > 0:
                    if val < 128: #draw the number
                        textSurf = BIGFONT.render(str(val), True, TXT1 if val < 8 else TXT2)
                    else: #draw smaller
                        textSurf = BASICFONT.render(str(val), True, TXT1 if val < 8 else TXT2)
                    textRect = textSurf.get_rect()
                    textRect.center = left + int(BOXSIZE /2), top + int(BOXSIZE /2)
                    DISPLAYSURF.blit(textSurf, textRect)
                
    
    for y in range(4):  #then draw shifted boxes on top
        for x in range(4):
            left, top = leftTopCoordsOfBox(x, y)
            left += shiftx
            top += shifty
            if shiftedBoxes[y][x] != 0: #display box shifted
                val = shiftedBoxes[y][x]
                pygame.draw.rect(DISPLAYSURF, colorDict[val], (left, top, BOXSIZE, BOXSIZE))
                
                if val < 128: #draw the number
                    textSurf = BIGFONT.render(str(val), True, TXT1 if val < 8 else TXT2)
                else: #draw smaller
                    textSurf = BASICFONT.render(str(val), True, TXT1 if val < 8 else TXT2)
                textRect = textSurf.get_rect()
                textRect.center = left + int(BOXSIZE /2), top + int(BOXSIZE /2)
                DISPLAYSURF.blit(textSurf, textRect)
            
    pygame.display.update()
    FPSCLOCK.tick(FPS)


    
def addNew(board):
    #populates one random spot with a new 2 or 4

    if hasSpaceLeft(board):
        freeSpots = []
        for y in range(4):
            for x in range(4):
                if board[y][x] == 0:
                    freeSpots.append((y, x))
        if len(freeSpots) > 0:
            newSpot = choice(freeSpots)
            if randint(0, 10) == 7:
                board[newSpot[0]][newSpot[1]] = 4
            else:
                board[newSpot[0]][newSpot[1]] = 2 # about 1 in ten is a 4

        #popup animation:        
        left, top = leftTopCoordsOfBox(newSpot[1], newSpot[0])
        val = board[newSpot[0]][newSpot[1]]
        inc = int(BOXSIZE/8)
        for i in range(2, -1, -1):
            pygame.draw.rect(DISPLAYSURF, colorDict[val], (left+ (inc * i), top + (inc * i), BOXSIZE - (inc * 2 * i), BOXSIZE - (inc * 2 * i)))
            pygame.display.update()
            FPSCLOCK.tick(FPS)
    return board


def slideLeft(board):
    beforeMove = deepcopy(board)
    def oneShift():
        boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        origBoard = deepcopy(board)
        for y in range(4):
            for x in range(3):
                if board[y][x] == 0:
                    boxesToShift[y][x+1:] = board[y][x+1:]
                    board[y].pop(x)
                    board[y].append(0)
                    break

        shiftBoxes(origBoard, boxesToShift, "left")

    for x in range(3):
        oneShift()
    
    boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    origBoard = deepcopy(board)
    extraShift = False
    for y in range(4):
            if board[y][0]!= 0 and board[y][0] == board[y][1]:
                if board[y][2] != 0 and board[y][2] == board[y][3]:
                    extraShift = True
                    boxesToShift[y][1] = board[y][1] 
                    boxesToShift[y][3] = board[y][3]
                    board[y] = [board[y][0] * 2, 0, board[y][3] * 2, 0]
                else:
                    boxesToShift[y][1:] = board[y][1:]
                    board[y].pop(0)
                    board[y].append(0)
                    board[y][0] *= 2
            elif board[y][1]!= 0 and board[y][1] == board[y][2]:
                boxesToShift[y][2:] = board[y][2:]
                board[y].pop(1)
                board[y].append(0)
                board[y][1] *= 2
            elif board[y][2]!= 0 and board[y][2] == board[y][3]:
                boxesToShift[y][3] = board[y][3]
                board[y].pop(2)
                board[y].append(0)
                board[y][2] *= 2

    shiftBoxes(origBoard, boxesToShift, "left")
    if extraShift:
        oneShift()
    drawBoxes(board)

    if beforeMove == board:
        return False
    return True
    
def slideRight(board):
    
    beforeMove = deepcopy(board)
    def oneShift():
        boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        origBoard = deepcopy(board)
        for y in range(4):
            for x in range(3, 0, -1):
                if board[y][x] == 0:
                    boxesToShift[y][:x] = board[y][:x]
                    board[y].pop(x)
                    board[y].insert(0, 0)
                    break

        shiftBoxes(origBoard, boxesToShift, "right")

    for x in range(3):
        oneShift()
    
    boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    origBoard = deepcopy(board)
    extraShift = False
    for y in range(4):
            if board[y][3]!= 0 and board[y][3] == board[y][2]:
                if board[y][1] != 0 and board[y][1] == board[y][0]:
                    extraShift = True
                    boxesToShift[y][0] = board[y][0] 
                    boxesToShift[y][2] = board[y][2]
                    board[y] = [0, board[y][1] * 2, 0, board[y][3] * 2]
                else:
                    boxesToShift[y][:3] = board[y][:3]
                    board[y].pop(3)
                    board[y].insert(0, 0)
                    board[y][3] *= 2
            elif board[y][2]!= 0 and board[y][2] == board[y][1]:
                boxesToShift[y][:2] = board[y][:2]
                board[y].pop(2)
                board[y].insert(0, 0)
                board[y][2] *= 2
            elif board[y][1]!= 0 and board[y][1] == board[y][0]:
                boxesToShift[y][0] = board[y][0]
                board[y].pop(1)
                board[y].insert(0, 0)
                board[y][1] *= 2

    shiftBoxes(origBoard, boxesToShift, "right")
    if extraShift:
        oneShift()
    drawBoxes(board)
    if beforeMove == board:
        return False
    return True
    


def slideDown(board):
    beforeMove = deepcopy(board)
    def oneShift():
        boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        origBoard = deepcopy(board)
        for x in range(4):
            for y in range(3, 0, -1):
                if board[y][x] == 0:
                    for y2 in range(y, -1, -1):
                        boxesToShift[y2][x] = board[y2][x]
                    for y2 in range(y, 0, -1):
                        board[y2][x] = board[y2-1][x]
                    board[0][x] = 0
                    break

        shiftBoxes(origBoard, boxesToShift, "down")
    
    for x in range(3):
        oneShift()
    
    boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    origBoard = deepcopy(board)
    extraShift = False
    for x in range(4):
            if board[3][x]!= 0 and board[3][x] == board[2][x]:  # two merges in one col
                if board[1][x] != 0 and board[1][x] == board[0][x]:
                    extraShift = True
                    boxesToShift[2][x] = board[2][x] 
                    boxesToShift[0][x] = board[0][x]
                    board[0][x] = 0
                    board[1][x] *= 2
                    board[2][x] = 0
                    board[3][x] *= 2
                else:  #just the bottom two rows merge
                    boxesToShift[2][x] = board[2][x]
                    boxesToShift[1][x] = board[1][x]
                    boxesToShift[0][x] = board[0][x]
                    board[3][x] *= 2
                    board[2][x] = board[1][x]
                    board[1][x] = board[0][x]
                    board[0][x] = 0
            elif board[2][x]!= 0 and board[2][x] == board[1][x]: #middle rows merge
                boxesToShift[1][x] = board[1][x]
                boxesToShift[0][x] = board[0][x]
                board[2][x] *= 2
                board[1][x] = board[0][x]
                board[0][x] = 0
            elif board[1][x] != 0 and board[1][x] == board[0][x]: #just top two merge
                boxesToShift[0][x] = board[0][x]
                board[1][x] *= 2
                board[0][x] = 0

    shiftBoxes(origBoard, boxesToShift, "down")
    if extraShift:
        oneShift()
    
    drawBoxes(board)
    if beforeMove == board:
        return False
    return True

def slideUp(board):
    beforeMove = deepcopy(board)
    def oneShift():
        boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
        origBoard = deepcopy(board)
        for x in range(4):
            for y in range(3):
                if board[y][x] == 0:
                    for y2 in range(y+1, 4):
                        boxesToShift[y2][x] = board[y2][x]
                    for y2 in range(y, 3):
                        board[y2][x] = board[y2+1][x]
                    board[3][x] = 0
                    break

        shiftBoxes(origBoard, boxesToShift, "up")
    
    for x in range(3):
        oneShift()
    
    boxesToShift = [[0,0,0,0],[0,0,0,0],[0,0,0,0],[0,0,0,0]]
    origBoard = deepcopy(board)
    extraShift = False
    for x in range(4):
            if board[0][x]!= 0 and board[0][x] == board[1][x]:  # two merges in one col
                if board[2][x] != 0 and board[2][x] == board[3][x]:
                    extraShift = True
                    boxesToShift[1][x] = board[1][x] 
                    boxesToShift[3][x] = board[3][x]
                    board[0][x] *= 2
                    board[1][x] = 0
                    board[2][x] *= 2
                    board[3][x] = 0
                else:  #just the top two rows merge
                    boxesToShift[1][x] = board[1][x]
                    boxesToShift[2][x] = board[2][x]
                    boxesToShift[3][x] = board[3][x]
                    board[0][x] *= 2
                    board[1][x] = board[2][x]
                    board[2][x] = board[3][x]
                    board[3][x] = 0
            elif board[2][x]!= 0 and board[2][x] == board[1][x]: #middle rows merge
                boxesToShift[2][x] = board[2][x]
                boxesToShift[3][x] = board[3][x]
                board[1][x] *= 2
                board[2][x] = board[3][x]
                board[3][x] = 0
            elif board[3][x] != 0 and board[3][x] == board[2][x]: #just bottom two merge
                boxesToShift[3][x] = board[3][x]
                board[2][x] *= 2
                board[3][x] = 0

    shiftBoxes(origBoard, boxesToShift, "up")
    if extraShift:
        oneShift()
    
    drawBoxes(board)
    if beforeMove == board:
        return False
    return True #something actually changed


def hasSpaceLeft(board):
    for y in range(4):
        for x in range(4):
            if board[y][x] == 0:
                return True
    return False

def checkLost(board):
    for y in range(3): #check below everything
        for x in range(4):
            if board[y][x] == board[y + 1][x]:
                return False
    for x in range(3): #check to right of everything
        for y in range(4):
            if board[y][x] == board[y][x+1]:
                return False
    return True

def loseAnimation():
    textSurf = BASICFONT.render("YOU LOSE.", True, TXT2)
    textRect = textSurf.get_rect()
    textRect.center = XMARGIN, int(YMARGIN / 2)
    DISPLAYSURF.blit(textSurf, textRect)
            
    pygame.display.update()
    pygame.time.wait(1500)

    
def leftTopCoordsOfBox(boxx, boxy):
    # Convert board coordinates to pixel coordinates
    left = boxx * (BOXSIZE + GAPSIZE) + XMARGIN
    top = boxy * (BOXSIZE + GAPSIZE) + YMARGIN
    return (left, top)

if __name__ == '__main__':
    main()
