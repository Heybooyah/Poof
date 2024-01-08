from images import images
import pygame
from utils.vector2 import Vector2
from utils.binarySearch import binarySearch
from graphics.animation import *
from utils.resizingFuncs import blitResized
from logic.song.timingPoints import getNextBeat, getPreviousBeat

class PlayerState:
    def __init__(self):
        self.time = None
        self.pos = None
        self.visiblePos = None
        self.lastMove = None
        self.lastCountedMove = None
        self.countedMovesMade = None
        self.acc = None
        self.deathTime = None
        self.gliding = False
        self.glideStartPos = None

class Player:
    offset = Vector2(5.9, 3.1) #TODO: Don't hardcode these values
    moveLength = 0.2
    def __init__(self, startPos, startTime):
        self.startPos = startPos
        self.startTime = startTime
                
        self.moves = [] #Tuple of (diff, time, isPress)
        
    def draw(self, win, state): 
        if state is None:
            return
        
        size = 100
        
        if state.lastMove is None:
            img = images.images["player_down"]
        else:
            if state.pos != state.visiblePos: #moving
                imgs = {
                    Vector2(-1, 0): images.images["player_left_moving"],
                    Vector2(0, -1): images.images["player_up_moving"],
                    Vector2(1, 0): images.images["player_right_moving"],
                    Vector2(0, 1): images.images["player_down_moving"]
                }
            else:
                imgs = {
                    Vector2(-1, 0): images.images["player_left"],
                    Vector2(0, -1): images.images["player_up"],
                    Vector2(1, 0): images.images["player_right"],
                    Vector2(0, 1): images.images["player_down"]
                }
            img = imgs[state.lastMove[0]]
        
        blitResized(win, img, self.offset, size, self.factor)
        #win.blit(pygame.transform.scale(img, size.toTuple()), (size * self.offset).toTuple())
        
    def move(self, diff, time):
        self.moves.append((diff, time, True))
        
    def stopMove(self, diff, time):
        self.moves.append((diff, time, False))

    def calculateState(self, level, searchTime):
        if searchTime < self.startTime:
            return None #cant have a state if the player isnt in the level yet
        
        def calculateAcc(currentAcc, movesMade, tileTime, time):
            thisAcc = abs(tileTime - time)
            return (currentAcc * (movesMade - 1) + thisAcc) / movesMade #weighted average
        
        def calculateGlideDistance(startTime, divisor, time): #returns tuple of (actual distance, visible distance)
            beatsElapsed = 0
            nextBeat = startTime
            while True:
                nextBeat = getNextBeat(level.timingPoints, nextBeat, divisor)
                if nextBeat > time:
                    break
                beatsElapsed += 1
            prevBeat = getPreviousBeat(level.timingPoints, nextBeat, divisor)
            visibleDistance = lerp(beatsElapsed, beatsElapsed + 1, prevBeat, nextBeat, time)
            actualDistance = round(visibleDistance)
            return(actualDistance, visibleDistance)
        
        def addPosMovesDeathTimeAcc(state):
            tilesMovedTo = set() #So you cant get acc counted twice off the same tile
            
            state.countedMovesMade = 0
            state.acc = 0
            
            state.pos = self.startPos.copy()
            currentTile = None
            
            tile = level.getTileAt(state.pos, self.startTime)
            if tile is None:
                state.deathTime = self.startTime
                return #If there's no tile at the start then you die at the start
            currentTile = tile #Otherwise that's the tile you're on

            for i, move in enumerate(self.moves):
                moveTime = move[1]
                if moveTime > searchTime:
                    return #If you've reached the time you want to, then you are alive and at your current pos
                
                if move[2] == False: #if your last move is a key release
                    if not state.gliding: #releasing a key only matters if you're gliding, if not then continue
                        continue
                    
                    glideStartTime = self.moves[i-1][1]
                    glideTile = level.getTileAt(state.glideStartPos, glideStartTime)
                    glideDistance = calculateGlideDistance(self.moves[i-1][1], glideTile.divisor, state.time)
                    state.pos = state.glideStartPos + move[0].multiply(glideDistance[0])
                    state.visiblePos = state.glideStartPos + move[0].multiply(glideDistance[1])
                
                state.lastMove = move
                
                tile = level.getTileAt(state.pos, moveTime)
                if tile != currentTile:
                    state.deathTime = currentTile.disappearTime + level.disappearLength #If you're not on the same tile as before when you start moving, then you died
                    return
                
                if tile.type == "glide":
                    
                
                state.pos += move[0] #Make the move you were trying to make
                tile = level.getTileAt(state.pos, moveTime)
                if tile is None:
                    state.deathTime = moveTime #If you move to nothing then you die at the time of your move
                    return
                
                currentTile = tile #Otherwise that's the tile you're on
                
                tileTuple = (tile.pos.x, tile.pos.y, tile.appearedTime, tile.disappearTime)
                if tileTuple not in tilesMovedTo:
                    tilesMovedTo.add(tileTuple)
                    state.lastCountedMove = move
                    state.countedMovesMade += 1
                    state.acc = calculateAcc(state.acc, state.countedMovesMade, tile.appearedTime, moveTime)
                
            tile = level.getTileAt(state.pos, searchTime) #If your last move was made before the search time
            if tile != currentTile:
                state.deathTime = currentTile.disappearTime + level.disappearLength #If you're not on the same tile as before, then you died
                return
        
        def addVisiblePos(state):
            time = state.deathTime if state.deathTime is not None else state.time
            lastMovePos = state.pos - state.lastMove[0] if state.lastMove is not None else Vector2(0, 0)
            lastMoveTime = state.lastMove[1] if state.lastMove is not None else self.startTime
            x = easeOutPow(lastMovePos.x, state.pos.x, lastMoveTime, lastMoveTime + self.moveLength, 3.5, min(time, lastMoveTime + self.moveLength))
            y = easeOutPow(lastMovePos.y, state.pos.y, lastMoveTime, lastMoveTime + self.moveLength, 3.5, min(time, lastMoveTime + self.moveLength))
            state.visiblePos = Vector2(x, y)
        
        state = PlayerState()
        state.time = searchTime
        addPosMovesDeathTimeAcc(state)
        if not state.gliding:
            addVisiblePos(state) #if it is gliding, the visible pos is already added in the other function
        return state