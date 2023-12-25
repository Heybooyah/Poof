from graphics import gui
from ui.button import Button
from ui.text import Text
from ui.scrollbar import Scrollbar
from logic.game import game

def show():
    gui.clear()
    update()

def hide():
    gui.clear()

def draw():
    objects.sort(key = lambda x : x.z)
    for object in objects:
        object.draw()
    for text in texts:
        text.draw()
    scrollbar.draw(gui.screen)

def startGame():
    hide()
    gui.setScreen("game")
    
def update():
    for object in objects:
        object.update()
    scrollbar.update()
        
def settings():
    hide()
    gui.setScreen("settings")
        
title = "Main Menu"
objects = [Button("Start", 100, 175, 100, 50, (0, 255, 0), (255, 0, 0), startGame, particles=True), Button("Settings", 100, 250, 100, 50, (0, 255, 0), (255, 0 ,0), settings),Button("Quit", 100, 325, 100, 50, (0, 255, 0), (255, 0, 0), quit)]
texts = [Text(title, 200, 100, (255, 0, 0), 50)]
#testing stuff here
scrollbar = Scrollbar(500, 50, 10, 200, "", [0,1,2,3])