from graphics import gui
from objects.tile import Tile
from objects.player import Player
from utils.vector2 import Vector2
from logic.level.level import Level
import input.input as input
import logic.song.songPlayer as songPlayer
from logic.song.timingPoints import TimingPoint, TimeSignature
from ui.text import Text
import json
import hashlib

tiles = None
level = None

def show():
    global level
    level.restart()
    update()
    
def hide():
    gui.clear()

def loadLevel(levelFile):
    global level
    songPlayer.unload()
    level = Level.fromFile(levelFile)
    
def checkSignature(data, signature):
    return hashlib.sha256(json.dumps(data).encode()).hexdigest() == signature

def checkInput():
    if input.keyActionBindings["left"].justPressed:
        level.player.move(Vector2(-1, 0), input.keyActionBindings["left"].songTimeLastPressed)
    elif input.keyActionBindings["left"].justReleased:
        level.player.stopMove(Vector2(-1, 0), input.keyActionBindings["left"].songTimeLastReleased)
    
    if input.keyActionBindings["right"].justPressed:
        level.player.move(Vector2(1, 0), input.keyActionBindings["right"].songTimeLastPressed)
    elif input.keyActionBindings["right"].justReleased:
        level.player.stopMove(Vector2(1, 0), input.keyActionBindings["right"].songTimeLastReleased)
        
    if input.keyActionBindings["up"].justPressed:
        level.player.move(Vector2(0, -1), input.keyActionBindings["up"].songTimeLastPressed)
    elif input.keyActionBindings["up"].justReleased:
        level.player.stopMove(Vector2(0, -1), input.keyActionBindings["up"].songTimeLastReleased)
        
    if input.keyActionBindings["down"].justPressed:
        level.player.move(Vector2(0, 1), input.keyActionBindings["down"].songTimeLastPressed)
    elif input.keyActionBindings["down"].justReleased:
        level.player.stopMove(Vector2(0, 1), input.keyActionBindings["down"].songTimeLastReleased)

def updateFactors(factor):
    level.factor = factor

def update():
    checkInput()
    
def draw():
    global accText
    timeSourceTime = songPlayer.getPos()
    
    playerState = level.player.calculateState(level, timeSourceTime)
    if playerState.deathTime is None:
        level.draw(gui.screen, timeSourceTime, playerState.visiblePos - Player.offset, level.tileSize, drawPlayer=True, playerState=playerState)
    elif playerState.deathTime + level.deathTimeBuffer >= timeSourceTime:
        level.draw(gui.screen, timeSourceTime, playerState.visiblePos - Player.offset, level.tileSize)
    else:
        level.restart()
    
    accText.text = f"{int(playerState.acc * 1000)}ms"
    accText.draw()
        
accText = Text("0ms", 100, 100)