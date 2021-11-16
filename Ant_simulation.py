import pygame as pg
from textwrap import wrap
import time
import sqlite3
from math import sin, cos, atan2, degrees, radians
from random import randint, random


"""
Ant simulation
by Jonas Ganderton
"""


# Set up pygame window and other aspects
pg.init()
screenX = 500  # If size is increased the main menu image could either be centred, or has to be redone, options menu also is left alligned
screenY = 500
screen = pg.display.set_mode((screenX, screenY))
trailScreen = pg.Surface((screenX, screenY), pg.SRCALPHA)
foodScreen = pg.Surface((screenX, screenY), pg.SRCALPHA)

titleFont = pg.font.Font("Comfortaa.ttf", 40)
font = pg.font.Font('Comfortaa.ttf', 30)
captionFont = pg.font.Font('Comfortaa.ttf', 20)

pg.display.set_caption("Ant simulator")
icon = pg.image.load("Images/ant_icon.png")
icon = pg.transform.scale(icon, (25, 27))
pg.display.set_icon(icon)

pg.display.update()

# All leaf images
leafDict = {1: "L1.png", 2: "L2.png", 3: "L3.png", 4: "L4.png", 5: "L5.png", 6: "L6.png", 7: "L7.png", 8: "L8.png", 9: "L9.png",
            10: "L10.png", 11: "L11.png", 12: "L12.png", 13: "L13.png", 14: "L14.png", 15: "L15.png", 16: "L16.png", 17: "L17.png", 18: "L18.png",
            19: "L19.png", 20: "L20.png", 21: "L21.png", 22: "L22.png", 23: "L23.png", 24: "L24.png", 25: "L25.png", 26: "L26.png", 27: "L27.png",
            28: "L28.png", 29: "L29.png", 30: "L30.png", 31: "L31.png", 32: "L32.png", 33: "L33.png", 34: "L34.png", 35: "L35.png", 36: "L36.png",
            37: "L37.png", 38: "L38.png", 39: "L39.png", 40: "L40.png", 41: "L41.png", 42: "leaf.png"}

# Slider descriptions
descriptions = ["The number of ants at the start of a simulation",
                "The number of food items that will be on the screen for ants to find",
                "The distance that ants move in one step",
                "Ants may turn anywhere upto this value either left or right",
                "The length of the pheromone trail left by each ant",
                "The strength of the trail left by an ant carrying food",
                "The strength of the trail left by an ant wandering around",
                "The probability of an ant following a trail",
                "The number of food items that need to be collected for a new ant to be born"]

WHITE = (255, 255, 255)
GREEN_OFF = (92, 247, 134)
GREEN_ON = (15, 186, 61)
GREEN = (101, 223, 80)
ORANGE_OFF = (250, 210, 120)
ORANGE_ON = (250, 182, 47)
MENU_ORANGE = (250, 191, 82)
BROWN = (69, 30, 30)
BLACK = (0, 0, 0)
BLACK_ALPHA = (0, 0, 0, 0)
RED = (252, 56, 56)

screen.fill(MENU_ORANGE)

# For random facts
factDoc = open("ant_facts.txt", "r")
facts = factDoc.read().split("\n")

# Set up database connection
db = sqlite3.connect("AntSimulation.db")
c = db.cursor()
c.execute("""CREATE TABLE IF NOT EXISTS
             statistics (id INTEGER PRIMARY KEY, startAntNum INTEGER, endAntNum INTEGER, foodCollected INTEGER, timeTaken INTEGER)""")

# - - - User variables - - - #
USER_antNum = 15  # starting number of ants
USER_foodNum = 5
USER_antSpeed = 5  # Distance ant walks in each step (pixels)
USER_maxTurn = 20  # Maximum angle an ant can turn left or right in one step
USER_trailLength = 40  # Number of trail segments
USER_foodTrailStrength = 60  # Strength of trail when carrying food
USER_trailStrength = 15  # Strength of trail when searching
USER_trailFollowChance = 0.3  # Base chance of following a trail
USER_untilNextAnt = 15  # Adds ant after this many items of food collected

foodSpeedIncrease = 1.4  # Not a user variable as this is better as a constant
antFoodSpeed = USER_antSpeed * foodSpeedIncrease
page = 1

# Rest of program
class Button:  # Use inheritance to have a button class for all buttons, and a new class for menu buttons
    def __init__(self, position, dimensions, title, offColour, onColour, mini=False, delete=False, leftAlign=False):
        self.position = position
        self.dimensions = dimensions
        self.title = title
        self.offColour = offColour
        self.onColour = onColour
        self.mini = mini
        self.scrollOn = False
        self.leftAlign = leftAlign
        if delete:
            self.colour = RED
        else:
            self.colour = WHITE

        if self.leftAlign:
            self.dimensions = (captionFont.render(self.title, True, self.colour).get_rect().width + 20, dimensions[1])

    def drawOffButton(self):
        # When mouse scrolls off
        pg.draw.rect(screen, (self.offColour), (self.position[0], self.position[1], self.dimensions[0], self.dimensions[1]))
        # , (0,0,0)) shows the text box/highlights text
        if self.mini:
            text = captionFont.render(self.title, True, self.colour)
        else:
            text = font.render(self.title, True, self.colour)

        textY = text.get_rect().height
        if not self.leftAlign:
            textX = text.get_rect().width
            screen.blit(text, (self.position[0] + (self.dimensions[0] - textX) / 2, self.position[1] + (self.dimensions[1] - textY) / 2))
        else:
            screen.blit(text, (self.position[0] + 10, self.position[1] + (self.dimensions[1] - textY) / 2))
        pg.display.update()

    def drawOnButton(self):
        # When mouse scrolls over
        pg.draw.rect(screen, (self.onColour), (self.position[0], self.position[1], self.dimensions[0], self.dimensions[1]))
        if self.mini:
            text = captionFont.render(self.title, True, self.colour)
        else:
            text = font.render(self.title, True, self.colour)

        textY = text.get_rect().height
        if not self.leftAlign:
            textX = text.get_rect().width
            screen.blit(text, (self.position[0] + (self.dimensions[0] - textX) / 2, self.position[1] + (self.dimensions[1] - textY) / 2))
        else:
            screen.blit(text, (self.position[0] + 10, self.position[1] + (self.dimensions[1] - textY) / 2))
        pg.display.update()

    def mouseOn(self, pgEvent):
        # Check if mouse is on
        try:
            if pgEvent.dict["pos"][0] >= self.position[0] and pgEvent.dict["pos"][0] <= self.position[0] + self.dimensions[0]:
                if pgEvent.dict["pos"][1] >= self.position[1] and pgEvent.dict["pos"][1] <= self.position[1] + self.dimensions[1]:
                    if pgEvent.type == 1026 and pgEvent.dict["button"] == 1:
                        return 0
                    else:
                        self.drawOnButton()
                        self.scrollOn = True
                        return 2
                else:
                    self.drawOffButton()
                    self.scrollOn = False

            elif not (pgEvent.dict["pos"][0] >= self.position[0] and pgEvent.dict["pos"][0] <= self.position[0] + self.dimensions[0]):
                self.drawOffButton()
                self.scrollOn = False
            elif not (pgEvent.dict["pos"][1] >= self.position[1] and pgEvent.dict["pos"][1] <= self.position[1] + self.dimensions[1]):
                self.drawOffButton()
                self.scrollOn = False

        except KeyError:
            pass
            # If the mouse is not on the screen
        return 1


class Slider:
    """
    value = slider pos - left pos
    max value = right pos - selfpos

    slider width = 200

    if max value is 10, number of values  = 11 (including zero)
    every range of 20px  = 1 value, 0 remains at
    202 / 11 = 20

    if maxValue == 10:
        interval = (self.barSize[0] - self.indicatorSize[0]) / maxValue
        value = (sliderPos - leftPos) / interval
    """

    def __init__(self, position, label, default, maxValue=100, minValue=0):
        self.position = position
        self.label = label
        self.default = default  # value not position
        self.maxValue = maxValue + 1  # means range is zero to maxValue
        self.minValue = minValue
        self.barSize = (212, 30)
        self.indicatorSize = (10, 30)
        self.interval = (self.barSize[0] - self.indicatorSize[0]) / self.maxValue

    def drawSlider(self, value):
        pg.draw.rect(screen, ORANGE_OFF, (self.position[0], self.position[1], self.barSize[0], self.barSize[1]))
        pg.draw.rect(screen, ORANGE_ON, (value * self.interval + self.position[0], self.position[1], self.indicatorSize[0], self.indicatorSize[1]))
        # Value of the current slider
        text = captionFont.render(str(value), True, WHITE)
        screen.blit(text, (460, self.position[1] + 5))
        pg.display.update()

    def slide(self):
        value = 1
        while True:
            for event in pg.event.get():
                try:
                    if event.pos[0] < self.position[0] + self.barSize[0] - self.indicatorSize[0] and event.pos[0] > self.position[0]:
                        # Move slider according to mouse position
                        value = int((event.pos[0] - self.position[0]) / self.interval) + self.minValue
                        pg.draw.rect(screen, ORANGE_OFF, (self.position[0], self.position[1], self.barSize[0], self.barSize[1]))
                        pg.draw.rect(screen, ORANGE_ON, (event.pos[0], self.position[1], self.indicatorSize[0], self.indicatorSize[1]))

                        textX = 460
                        pg.draw.rect(screen, MENU_ORANGE, (textX, self.position[1], 40, 30))
                        text = captionFont.render(str(value), True, WHITE)
                        screen.blit(text, (textX, self.position[1] + 5))
                        pg.display.update()

                    if event.type == 1026 and event.dict["button"] == 1:
                        # If mouse up (no longer holding down)
                        return value
                except AttributeError as e:
                    pass



class Ant:
    def __init__(self, pos, heading):
        self.pos = pos
        self.heading = heading
        self.trailFollowChance = USER_trailFollowChance
        self.carryingFood = False
        self.trails = pg.Surface((screenX, screenY), pg.SRCALPHA)
        self.maxTurn = USER_maxTurn
        self.speed = USER_antSpeed
        self.pointer = 0
        self.lineList = []
        for _ in range(USER_trailLength):
            self.lineList.append([(0, 0), (0, 0), 0])  # Crashes when run at 0 trail length

    def drawTrails(self, startPos, endPos):
        if self.carryingFood:
            TRAIL_PURPLE = (124, 36, 240, USER_foodTrailStrength)
        else:
            TRAIL_PURPLE = (124, 36, 240, USER_trailStrength)

        self.lineList[self.pointer] = ((startPos[0], startPos[1]), (endPos[0], endPos[1]), TRAIL_PURPLE)

        # Draw newest line segment
        pg.draw.line(self.trails, self.lineList[self.pointer][2], self.lineList[self.pointer][0], self.lineList[self.pointer][1], 3)

        self.pointer += 1
        if self.pointer == USER_trailLength:
            self.pointer = 0

        # Draw over oldest line segment
        pg.draw.line(self.trails, BLACK_ALPHA, self.lineList[self.pointer][0], self.lineList[self.pointer][1], 3)

        trailScreen.blit(self.trails, (0, 0))

    def move(self):
        length = 1
        oldPos = self.pos

        foundTrail = False
        i = 0
        randomNumber = random()
        colour = BLACK
        if self.carryingFood:
            if (self.pos[0] - screenX / 2) ** 2 + (self.pos[1] - screenY / 2) ** 2 > 225:
                self.moveRandom()
                # If within centre 15 pixel radius don't move
                # This is for when lots of ants are used
                # The program can only process 1 food deposit/step
        else:
            while not foundTrail:
                leftX = round(self.pos[0] + length * sin(radians(self.heading - 45 * i)))
                leftY = round(self.pos[1] - length * cos(radians(self.heading - 45 * i)))
                rightX = round(self.pos[0] + length * sin(radians(self.heading + 45 * i)))
                rightY = round(self.pos[1] - length * cos(radians(self.heading + 45 * i)))
                try:
                    colourAlpha = trailScreen.get_at((leftX, leftY))
                    colour = colourAlpha[:3]
                except IndexError:
                    print(self.pos, (leftX, leftY))

                if colour != GREEN and colour != BLACK:
                    p = self.trailFollowChance + colourAlpha[3] / 255
                    if randomNumber < p:
                        self.heading -= 45 * i
                        self.fixHeading()
                        self.pos = (leftX, leftY)
                        if USER_trailLength > 0:
                            self.drawTrails(oldPos, self.pos)
                    else:
                        self.moveRandom()
                    foundTrail = True

                else:
                    colourAlpha = trailScreen.get_at((rightX, rightY))
                    colour = colourAlpha[:3]

                    if colour != GREEN and colour != BLACK:
                        p = self.trailFollowChance + colourAlpha[3] / 255
                        if randomNumber < p:
                            self.heading += 45 * i
                            self.fixHeading()
                            self.pos = (rightX, rightY)
                            if USER_trailLength > 0:
                                self.drawTrails(oldPos, self.pos)
                        else:
                            self.moveRandom()
                        foundTrail = True

                i += 1
                if i == 5 and not foundTrail:  # At i == 5 all 8 possible locations have been tested
                    self.moveRandom()
                    # if self.trailFollowChance < 1:
                    #     self.trailFollowChance += 0.1
                    break
                elif i == 5 or foundTrail:
                    self.blitHeading()
                    # if self.trailFollowChance > USER_trailFollowChance:
                    #    self.trailFollowChance -= 0.1

        return foundTrail

    def moveRandom(self):
        # Turn a bit left or right
        self.heading += randint(-self.maxTurn, self.maxTurn)
        self.fixHeading()

        oldPos = self.pos
        self.pos = (self.pos[0] + sin(radians(self.heading)) * self.speed, self.pos[1] - cos(radians(self.heading)) * self.speed)

        if USER_trailLength > 0:
            self.drawTrails(oldPos, self.pos)

        self.stopLeaving()
        self.blitHeading()

    def blitHeading(self):
        # Blits ant to screen depending on its heading
        if self.carryingFood:
            antImgList = antImgs_F
        else:
            antImgList = antImgs

        if self.heading > 158 or self.heading <= -158:
            screen.blit(antImgList[4], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > 112:
            screen.blit(antImgList[3], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > 68:
            screen.blit(antImgList[2], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > 22:
            screen.blit(antImgList[1], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > -22:
            screen.blit(antImgList[0], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > -68:
            screen.blit(antImgList[7], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > -112:
            screen.blit(antImgList[6], (self.pos[0] - 9, self.pos[1] - 9))
        elif self.heading > -158:
            screen.blit(antImgList[5], (self.pos[0] - 9, self.pos[1] - 9))
        else:
            print("Heading error")
            print(self.heading)

        # for debugging - dot on ant position
        # pg.draw.circle(screen, (0,0,0), (int(self.pos[0]), int(self.pos[1])), 5, True)


    def stopLeaving(self):
        # - - - If ant outside window - - - #
        antImgSize = 9  # image is square so only need one value

        # Off the left side
        if self.pos[0] < antImgSize:
            if self.pos[1] < antImgSize:
                self.pos = (antImgSize, antImgSize)
                self.heading += 180
            elif self.pos[1] > screenY - antImgSize:
                self.pos = (antImgSize, screenY - antImgSize)
                self.heading += 180
            else:
                self.pos = (antImgSize, self.pos[1])
                self.heading = -self.heading

        # Off the right side
        elif self.pos[0] > screenX - antImgSize:
            if self.pos[1] < antImgSize:
                self.pos = (screenX - antImgSize, antImgSize)
                self.heading -= 180
            elif self.pos[1] > screenY - antImgSize:
                self.pos = (screenX - antImgSize, screenY - antImgSize)
                self.heading -= 180
            else:
                self.pos = (screenX - antImgSize, self.pos[1])
                self.heading = -self.heading

        # Off the top or bottom
        elif self.pos[1] < antImgSize:
            self.pos = (self.pos[0], antImgSize)
            self.heading = 180 - self.heading
        elif self.pos[1] > 500 - antImgSize:
            self.pos = (self.pos[0], 500 - antImgSize)
            self.heading = 180 - self.heading

        self.fixHeading()

    def headTowards(self, otherPos):
        # Ant points towards food/nest within a radius
        xDiff = otherPos[0] - self.pos[0]
        yDiff = self.pos[1] - otherPos[1]
        self.heading = degrees(atan2(xDiff, yDiff))

    def fixHeading(self):
        # Fixes invalid headings - could make this into a function
        if self.heading > 180:
            self.heading -= 360
        elif self.heading < -180:
            self.heading += 360


class Food:
    def __init__(self, foodList):
        self.strength = 42
        self.pos = self.spawnFood(foodList)
        self.blitPos = (self.pos[0] - 28, self.pos[1] - 31)

    def spawnFood(self, foodList):
        clear = False
        while not clear:
            posX = randint(0, screenX - 58) + 28
            posY = randint(0, screenY - 65) + 31
            if (posX - 225 - 28) ** 2 + (posY - 215 - 31) ** 2 > 6084:
                if posX > 125 + 28 or (posY > 63 + 31 and posY < 500 - 64 - 31):
                    # Increase posX range if more space is needed
                    clear = True
                    for foodItems in foodList:
                        # Check if food is too near to any other pieces of food
                        if (posX - foodItems.pos[0]) ** 2 + (posY - foodItems.pos[1]) ** 2 < 8000:
                            clear = False
                            break
        return posX, posY

    def blitFood(self):
        foodScreen.blit(leafDict[self.strength], self.blitPos)
        # pg.draw.circle(foodScreen, WHITE, self.blitPos, 5)


def loadImgs():
    """
    N/E/S/W = North/East/South/West
    F = Food
    Means the program doesn't have to rotate an image for every ant not facing N or NE
    """
    # - - At 0 degrees - - #
    ant_N = pg.image.load("Images/ant_0.png")
    antF_N = pg.image.load("Images/ant_0_f_dark.png")

    # Rotations
    ant_E = pg.transform.rotate(ant_N, 270)
    ant_S = pg.transform.rotate(ant_N, 180)
    ant_W = pg.transform.rotate(ant_N, 90)

    antF_E = pg.transform.rotate(antF_N, 270)
    antF_S = pg.transform.rotate(antF_N, 180)
    antF_W = pg.transform.rotate(antF_N, 90)

    # - - Ant 45 degrees - - #
    ant_NE = pg.image.load("Images/ant_45.png")
    antF_NE = pg.image.load("Images/ant_45_f_dark.png")

    # Rotations
    ant_SE = pg.transform.rotate(ant_NE, 270)
    ant_SW = pg.transform.rotate(ant_NE, 180)
    ant_NW = pg.transform.rotate(ant_NE, 90)

    antF_SE = pg.transform.rotate(antF_NE, 270)
    antF_SW = pg.transform.rotate(antF_NE, 180)
    antF_NW = pg.transform.rotate(antF_NE, 90)

    global antImgs
    global antImgs_F
    antImgs = [ant_N, ant_NE, ant_E, ant_SE, ant_S, ant_SW, ant_W, ant_NW]
    antImgs_F = [antF_N, antF_NE, antF_E, antF_SE, antF_S, antF_SW, antF_W, antF_NW]

    for a in range(8):
        antImgs[a] = antImgs[a].convert_alpha()
        antImgs_F[a] = antImgs_F[a].convert_alpha()

    global leafDict
    for i in leafDict:
        leafDict[i] = pg.image.load("Images/" + leafDict[i]).convert_alpha()


#   =  =   =   =   =   =   =   =   =   =   =   Menu   =   =   =   =   =   =   =   =   =   =   =   #
def mainMenu():
    # screen.fill((250, 191, 82))
    menuBG = pg.image.load("Images/Main_menu.png")
    screen.blit(menuBG, (0, 0))
    text = titleFont.render("Ant simulator", True, WHITE)
    screen.blit(text, (screenX / 2 - text.get_rect().width / 2, 70))
    text = captionFont.render("By Jonas Ganderton", True, WHITE)
    screen.blit(text, (screenX / 2 - text.get_rect().width / 2, 130))

    buttonX = 250  # width
    buttonY = 45  # height
    firstButton = 166  # y pos of initial button

    runSim = Button((screenX / 2 - buttonX / 2, firstButton), (buttonX, buttonY), "Run simulation", ORANGE_OFF, ORANGE_ON)
    runSim.drawOffButton()

    options = Button((screenX / 2 - buttonX / 2, firstButton + (buttonY * 1.3)), (buttonX, buttonY), "Options", ORANGE_OFF, ORANGE_ON)
    options.drawOffButton()

    dataViewer = Button((screenX / 2 - buttonX / 2, firstButton + (buttonY * 2.6)), (buttonX, buttonY), "View data", ORANGE_OFF, ORANGE_ON)
    dataViewer.drawOffButton()

    close = Button((screenX / 2 - buttonX / 2, firstButton + (buttonY * 3.9)), (buttonX, buttonY), "Exit", ORANGE_OFF, ORANGE_ON)
    close.drawOffButton()

    runMenu = True

    while runMenu:
        for event in pg.event.get():
            pg.display.update()

            if event.type == pg.QUIT:
                runMenu = False

            if not runSim.mouseOn(event):
                data = simulation()
                statement = "UPDATE statistics SET endAntNum = " + str(data[0]) + ", foodCollected = " +str(data[1])
                statement += ", timeTaken = " + str(data[2]) + " WHERE id = " + str(data[3])
                c.execute(statement)
                db.commit()

                returnToMenu()
                pg.draw.rect(screen, MENU_ORANGE, (100, 160, 300, 255))

            elif not options.mouseOn(event):
                optionsMenu()
                returnToMenu()
                pg.draw.rect(screen, MENU_ORANGE, (100, 160, 300, 255))

            elif not dataViewer.mouseOn(event):
                global page
                page = 1
                while viewData():
                    pass
                    # If data is deleted, viewData() returns True so this allows it to run again, from the same page
                returnToMenu()
                pg.draw.rect(screen, MENU_ORANGE, (100, 160, 300, 255))

            elif not close.mouseOn(event):
                # pg.quit()
                runMenu = False


def returnToMenu():
    # Displays a random fact until a pygame event occurs
    menuBG = pg.image.load("Images/Main_menu.png")
    screen.blit(menuBG, (0, 0))

    text = titleFont.render("Ant simulator", True, WHITE)
    screen.blit(text, (screenX / 2 - text.get_rect().width / 2, 70))
    text = captionFont.render("By Jonas Ganderton", True, WHITE)
    screen.blit(text, (screenX / 2 - text.get_rect().width / 2, 130))

    factNum = randint(0, len(facts) - 1)

    text = font.render("Fact #" + str(factNum + 1), True, WHITE)
    screen.blit(text, (screenX / 2 - text.get_rect().width / 2, 190))

    splitLines = wrap(facts[factNum], 25)

    for line in range(len(splitLines)):
        text = captionFont.render(splitLines[line], True, WHITE)
        screen.blit(text, (screenX / 2 - text.get_rect().width / 2, 225 + 24 * line))  # font size = 20, spacing = 4

    pg.display.update()


#   =   =   =   =   =   =   =   =   =   =   =   Simulation   =   =   =   =   =   =   =   =   =   =   =   #
def simulation():
    global USER_untilNextAnt
    foodNum = 0
    screen.fill(GREEN)
    nestPos = (int(screenX / 2), int(screenY / 2))
    pg.draw.circle(screen, BROWN, nestPos, 35)
    menuButton = Button((10, 10), (100, 43), "Menu", GREEN_OFF, GREEN_ON)
    menuButton.drawOffButton()
    saved = captionFont.render("Saved!", True, WHITE)
    savedX = saved.get_rect().width

    # - - Create all necessary items - - #

    foodNum = 0
    foodList = []
    while foodNum < USER_foodNum:
        foodList.append(Food(foodList))
        foodNum += 1

    antNum = 0
    antList = []
    while antNum < USER_antNum:
        antList.append(Ant((screenX / 2, screenY / 2), randint(-180, 180)))
        antList[antNum].blitHeading()
        antNum += 1

    global foodCollected
    foodCollected = 0

    untilNextAnt = USER_untilNextAnt

    pg.display.update()

    # - - Simulation - - #
    startTime = time.time()
    saveTime = startTime + 600 # 10 minutes
    startMessage = 0
    runSimulation = True
    c.execute("""INSERT INTO statistics(startAntNum, endAntNum, foodCollected, timeTaken)
              VALUES (?,?,?,?)""", (USER_antNum, USER_antNum, 0, 0))
    c.execute("SELECT * FROM statistics")
    allData = c.fetchall()
    # This works since the id is always increasing, and never a previous id which has been deleted
    simID = allData[len(allData) - 1][0]
    while runSimulation:
        if time.time() >= saveTime:
            statement = "UPDATE statistics SET endAntNum = " + str(len(antList)) + ", foodCollected = " + str(foodCollected)
            statement += ", timeTaken = " + str(round(time.time() - startTime)) + " WHERE id = " + str(simID)
            c.execute(statement)
            db.commit()
            saveTime += 600
            # Save every 10 minutes
            startMessage = time.time()

        screen.fill(GREEN)
        pg.draw.circle(screen, BROWN, nestPos, 35)

        # - - Draw all necessary items - - #
        foodScreen.fill(BLACK_ALPHA)
        for food in range(len(foodList)):
            if foodList[food].strength <= 2:
                # <= 0 since if multiple ants reach food at the same time its strength will become negative
                # Changed from 0 to 2 since ants took a very long time to collide with the leaf stalk
                del(foodList[food])
                foodList.append(Food(foodList))
            else:
                foodList[food].blitFood()

        trailScreen.fill(BLACK_ALPHA)
        screen.blit(foodScreen, (0, 0))

        for ants in antList:
            ants.move()

        screen.blit(trailScreen, (0, 0))

        # Menu button
        if menuButton.scrollOn:
            menuButton.drawOnButton()
        else:
            menuButton.drawOffButton()

        text = captionFont.render("Food: " + str(foodCollected), True, WHITE)
        screen.blit(text, (15, screenY - 30))
        text = captionFont.render("Ants: " + str(len(antList)), True, WHITE)
        screen.blit(text, (15, screenY - 58))  # 60 seems too high up

        if time.time() - 0.7 <= startMessage:
            screen.blit(saved, (490 - savedX, 470))
            # Displays "Saved!" in bottom right corner for 0.7s after saving

        pg.display.update()

        # Check to see if ants can eat anything
        foodThisStep = checkForFood(antList, foodList)
        # If USER_untilNextAnt is 0, don't spawn new ants
        if foodThisStep != 0 and USER_untilNextAnt != 0:
            untilNextAnt -= foodThisStep

            while untilNextAnt <= 0:
                try:
                    # Spawn new ant
                    antList.append(Ant((screenX / 2, screenY / 2), randint(-180, 180)))
                    antList[len(antList) - 1].blitHeading()
                    untilNextAnt += USER_untilNextAnt

                except pg.error:
                    # pygame.error: Out of memory
                    # Stops the program adding an ant if that ant would cause the program to crash
                    USER_untilNextAnt = 0
                    untilNextAnt = 1
                    # These stops the if and while loops from running

        for event in pg.event.get():
            if not menuButton.mouseOn(event):
                runSimulation = False

    return len(antList), foodCollected, round(time.time() - startTime), simID


def checkForFood(allAnts, allFood):
    foodThisStep = 0
    for ant in allAnts:
        if ant.carryingFood:
            # If ant that is carrying food enters the nest
            if (ant.pos[0] - screenX / 2) ** 2 + (ant.pos[1] - screenY / 2) ** 2 <= 1225:
                ant.carryingFood = False
                global foodCollected
                foodCollected += 1
                foodThisStep += 1
                ant.maxTurn = USER_maxTurn
                ant.speed = USER_antSpeed

        else:
            try:
                for food in allFood:
                    # If ant near any food
                    if (ant.pos[0] - food.pos[0]) ** 2 + (ant.pos[1] - food.pos[1]) ** 2 <= 1225:  # Could increase this distance (radius^2)
                        colour = foodScreen.get_at((int(ant.pos[0]), int(ant.pos[1])))
                        if colour != (0, 0, 0, 0):
                            ant.carryingFood = True
                            ant.headTowards((screenX / 2, screenY / 2))
                            ant.maxTurn = 0
                            ant.speed = antFoodSpeed
                            food.strength -= 1
                        else:
                            # Point the ant towards certain places depending on how much leaf is left
                            if food.strength < 20:
                                ant.headTowards((food.pos[0] + 15, food.pos[1] + 20))
                                # Head towards the top of the stalk
                            else:
                                ant.headTowards(food.pos)
                                # Head towards the centre of the leaf

            except IndexError:
                pass
    return foodThisStep


#   =   =   =   =   =   =   =   =   =   =   =   Option menu   =   =   =   =   =   =   =   =   =   =   =   #
def optionsMenu():
    screen.fill((250, 191, 82))
    title = titleFont.render("Options", True, WHITE)
    screen.blit(title, (screenX / 2 - title.get_rect().width / 2, 50))

    textX = 140
    textY = 25
    textWidth = 350
    textHeight = 85

    # - - Globalise variables - - #
    global USER_antNum
    global USER_foodNum
    global USER_antSpeed
    global USER_maxTurn
    global USER_trailLength
    global USER_foodTrailStrength
    global USER_trailStrength
    global USER_trailFollowChance
    global USER_untilNextAnt

    # - - Create sliders - - #
    gap = 40
    startX = 240
    startY = 120
    "object = Slider(pos, label, variable, max, min)"
    # Some sliders have maximum values different to the final result due to rounding problems
    antNum = Slider((startX, startY), "Starting ants", USER_antNum, 99, 1)
    foodNum = Slider((startX, startY + gap), "Pieces of food", USER_foodNum, 10)  # 10 seems high so user doesn't need many at all
    antSpeed = Slider((startX, startY + gap * 2), "Ant speed", USER_antSpeed, 29, 1)  # 30 keeps speed within reason, window is only 500x500
    maxTurn = Slider((startX, startY + gap * 3), "Maximum turn", USER_maxTurn, 180)
    trailLength = Slider((startX, startY + gap * 4), "Trail length", USER_trailLength, 200)  # Trail decay rate
    foodTrailStrength = Slider((startX, startY + gap * 5), "Food trail strength", USER_foodTrailStrength, 257, -1)
    trailStrength = Slider((startX, startY + gap * 6), "Trail strength", USER_trailStrength, 257, -1)  # RGBA values go up to 255
    trailFollowChance = Slider((startX, startY + gap * 7), "Trail follow chance", USER_foodTrailStrength * 10, 10)
    untilNextAnt = Slider((startX, startY + gap * 8), "Food until new ant", USER_untilNextAnt)

    # - - Draw sliders - - #
    antNum.drawSlider(USER_antNum)
    foodNum.drawSlider(USER_foodNum)
    antSpeed.drawSlider(USER_antSpeed)
    maxTurn.drawSlider(USER_maxTurn)
    trailLength.drawSlider(USER_trailLength)
    foodTrailStrength.drawSlider(USER_foodTrailStrength)
    trailStrength.drawSlider(USER_trailStrength)
    trailFollowChance.drawSlider(int(USER_trailFollowChance * 10))
    untilNextAnt.drawSlider(USER_untilNextAnt)

    # Hover over buttons
    hoverStartX = 15
    antNumB = Button((hoverStartX, startY), (200, 30), "Starting ants", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    foodNumB = Button((hoverStartX, startY + gap * 1), (200, 30), "Pieces of food", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    antSpeedB = Button((hoverStartX, startY + gap * 2), (200, 30), "Ant speed", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    maxTurnB = Button((hoverStartX, startY + gap * 3), (200, 30), "Maximum turn", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    trailLengthB = Button((hoverStartX, startY + gap * 4), (200, 30), "Trail length", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    foodTrailStrengthB = Button((hoverStartX, startY + gap * 5), (200, 30), "Food trail strength", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    trailStrengthB = Button((hoverStartX, startY + gap * 6), (200, 30), "Trail strength", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    trailFollowChanceB = Button((hoverStartX, startY + gap * 7), (200, 30), "Trail follow chance", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)
    untilNextAntB = Button((hoverStartX, startY + gap * 8), (200, 30), "Food until new ant", MENU_ORANGE, ORANGE_ON, True, leftAlign=True)

    infoButtons = [antNumB, foodNumB, antSpeedB, maxTurnB, trailLengthB, foodTrailStrengthB, trailStrengthB, trailFollowChanceB, untilNextAntB]
    for button in infoButtons:
        button.drawOffButton()

    # - - Run the options - - #
    menuButton = Button((10, 10), (100, 43), "Menu", ORANGE_OFF, ORANGE_ON)
    menuButton.drawOffButton()
    pg.display.update()

    run = True
    while run:
        for event in pg.event.get():
            if not menuButton.mouseOn(event):
                run = False

            showText = False
            for button in infoButtons:
                if button.mouseOn(event) != 1:
                    # Allows either 0 (clicked) or 2 (hovering over)
                    buttonNum = infoButtons.index(button)
                    showText = True
                    break

            if showText:
                infoBox(buttonNum, textX, textY, textWidth, textHeight)
            else:
                pg.draw.rect(screen, MENU_ORANGE, (textX, textY, textWidth, textHeight))
                screen.blit(title, (screenX / 2 - title.get_rect().width / 2, 50))
                pg.display.update()
                # Ensures info text isn't left up in case the mouse is removed from the window without a pygame event

            if event.type == 1025 and event.dict["button"] == 1:  # Left mouse button down
                xPos = event.pos[0]
                yPos = event.pos[1]
                if xPos >= startX and xPos <= startX + 200:  # All sliders have the same x positions
                    if yPos >= 120 and yPos <= 150:
                        USER_antNum = antNum.slide()
                    elif yPos >= 120 + gap and yPos <= 150 + gap:
                        USER_foodNum = foodNum.slide()
                    elif yPos >= 120 + gap * 2 and yPos <= 150 + gap * 2:
                        USER_antSpeed = antSpeed.slide()
                        global antFoodSpeed
                        antFoodSpeed = USER_antSpeed * foodSpeedIncrease
                    elif yPos >= 120 + gap * 3 and yPos <= 150 + gap * 3:
                        USER_maxTurn = maxTurn.slide()
                    elif yPos >= 120 + gap * 4 and yPos <= 150 + gap * 4:
                        USER_trailLength = trailLength.slide()
                    elif yPos >= 120 + gap * 5 and yPos <= 150 + gap * 5:
                        USER_foodTrailStrength = foodTrailStrength.slide()
                    elif yPos >= 120 + gap * 6 and yPos <= 150 + gap * 6:
                        USER_trailStrength = trailStrength.slide()
                    elif yPos >= 120 + gap * 7 and yPos <= 150 + gap * 7:
                        USER_trailFollowChance = trailFollowChance.slide() / 10
                    elif yPos >= 120 + gap * 8 and yPos <= 150 + gap * 8:
                        USER_untilNextAnt = untilNextAnt.slide()
            if USER_trailLength == 0:
                USER_trailLength = 1

def infoBox(varNum, startX, startY, width, height):
    """
    Update user variable to include a description
    Could be in a slider class or in a dictionary{"variable":"description"}
    """
    pg.draw.rect(screen, MENU_ORANGE, (startX, startY, width, height))
    splitLines = wrap(descriptions[varNum], 30)
    gap = 30

    for line in range(len(splitLines)):
        text = captionFont.render(splitLines[line], True, WHITE)
        screen.blit(text, ((2 * startX + width - text.get_rect().width) / 2, startY + gap * line))

def viewData():
    # Setting up
    drawBoxes()
    db = sqlite3.connect("AntSimulation.db")
    c = db.cursor()
    c.execute("SELECT * FROM statistics")
    data = c.fetchall()

    menuButton = Button((30, 15), (100, 43), "Menu", ORANGE_OFF, ORANGE_ON)
    menuButton.drawOffButton()

    title = titleFont.render("View data", True, WHITE)
    screen.blit(title, (screenX / 2 - title.get_rect().width / 2, 15))

    # Set up table
    linesPerPage = 8
    gap = 40
    startAntX = 30
    finishAntX = 140
    foodX = 250
    timeX = 360
    headerY = 80
    subHeaderY = 105
    startY = 140

    lineNum = len(data)
    pageNum = lineNum // linesPerPage
    if lineNum % linesPerPage != 0:
        pageNum += 1
    global page

    if page > pageNum:
        page -= 1
        # This is for when the final piece of data on a page is deleted
        # Meaning that the page should no longer be able to view

    column = captionFont.render("Starting", True, WHITE)
    screen.blit(column, ((finishAntX + startAntX - column.get_rect().width) / 2, headerY))
    column = captionFont.render("ants", True, WHITE)
    screen.blit(column, ((finishAntX + startAntX - column.get_rect().width) / 2, subHeaderY))

    column = captionFont.render("Ending", True, WHITE)
    screen.blit(column, ((foodX + finishAntX - column.get_rect().width) / 2, headerY))
    column = captionFont.render("ants", True, WHITE)
    screen.blit(column, ((foodX + finishAntX - column.get_rect().width) / 2, subHeaderY))

    column = captionFont.render("Food", True, WHITE)
    screen.blit(column, ((timeX + foodX - column.get_rect().width) / 2, headerY))
    column = captionFont.render("found", True, WHITE)
    screen.blit(column, ((timeX + foodX - column.get_rect().width) / 2, subHeaderY))

    column = captionFont.render("Time", True, WHITE)
    screen.blit(column, ((470 + timeX - column.get_rect().width) / 2, headerY))
    column = captionFont.render("taken", True, WHITE)
    screen.blit(column, ((470 + timeX - column.get_rect().width) / 2, subHeaderY))

    currentPage = captionFont.render(str(page), True, WHITE)
    screen.blit(currentPage, ((screenX - currentPage.get_rect().width) / 2, 470))

    # Buttons
    previousPage = Button((30, 465), (110, 30), "Previous", ORANGE_OFF, ORANGE_ON, True)
    previousPage.drawOffButton()

    nextPage = Button((360, 465), (110, 30), "Next", ORANGE_OFF, ORANGE_ON, True)
    nextPage.drawOffButton()

    deleteButtonList = []
    for line in range(linesPerPage):
        deleteButtonList.append(Button((476, startY + 5 + line * gap), (20, 20), "x", ORANGE_OFF, ORANGE_ON, True, True))

    pg.display.update()
    run = True
    change = True

    boxStartY = 134
    boxWidth = 104
    boxHeight = 323
    while run:
        if change:
            pg.draw.rect(screen, ORANGE_OFF, (startAntX + 4, boxStartY, boxWidth, boxHeight))
            pg.draw.rect(screen, ORANGE_OFF, (finishAntX + 4, boxStartY, boxWidth, boxHeight))
            pg.draw.rect(screen, ORANGE_OFF, (foodX + 4, boxStartY, boxWidth, boxHeight))
            pg.draw.rect(screen, ORANGE_OFF, (timeX + 4, boxStartY, boxWidth, boxHeight))
            pg.draw.rect(screen, MENU_ORANGE, (200, 465, 100, 35))
            pg.draw.rect(screen, MENU_ORANGE, (476, startY + 5, 20, 320))

            # Display data
            linesDisplayed = 0
            for line in range(linesPerPage):
                try:
                    dataLocation = line + (page - 1) * linesPerPage
                    startAnts = font.render(str(data[dataLocation][1]), True, WHITE)
                    endAnts = font.render(str(data[dataLocation][2]), True, WHITE)
                    food = font.render(str(data[dataLocation][3]), True, WHITE)
                    totalTime = data[dataLocation][4]

                    minutes = str(totalTime % 3600 // 60)
                    seconds = str(totalTime % 3600 % 60)
                    if len(seconds) == 1:
                        seconds = "0" + seconds

                    if totalTime // 3600 > 0:
                        hours = str(totalTime // 3600)
                        if len(minutes) == 1:
                            minutes = "0" + minutes
                        time = font.render(hours + ":" + minutes + ":" + seconds, True, WHITE)
                    else:
                        time = font.render(minutes + ":" + seconds, True, WHITE)

                    screen.blit(startAnts, ((finishAntX + startAntX - startAnts.get_rect().width) / 2, startY + line * gap))
                    screen.blit(endAnts, ((foodX + finishAntX - endAnts.get_rect().width) / 2, startY + line * gap))
                    screen.blit(food, ((timeX + foodX - food.get_rect().width) / 2, startY + line * gap))
                    screen.blit(time, ((470 + timeX - time.get_rect().width) / 2, startY + line * gap))

                    deleteButtonList[line].drawOffButton()
                    linesDisplayed += 1
                except IndexError:
                    pass
                    # Occurs on the final page when less than 8 pieces of data are available
            currentPage = captionFont.render(str(page), True, WHITE)
            screen.blit(currentPage, ((screenX - currentPage.get_rect().width) / 2, 470))
            change = False
            pg.display.update()

        for event in pg.event.get():
            if not menuButton.mouseOn(event):
                run = False
            elif not previousPage.mouseOn(event):
                if page > 1:
                    page -= 1
                    change = True
            elif not nextPage.mouseOn(event):
                if page < pageNum:
                    page += 1
                    change = True
            else:
                for line in range(linesDisplayed):
                    if not deleteButtonList[line].mouseOn(event):
                        id = line + linesPerPage * (page - 1)
                        confirmDelete(data[id])

                        return True


def confirmDelete(dataToDelete):
    screen.fill(MENU_ORANGE)

    # Display warning message
    warning = titleFont.render("WARNING", True, RED)
    message1 = font.render("Are you sure you want", True, RED)
    message2 = font.render("to delete this data?", True, RED)

    screen.blit(warning, (screenX / 2 - warning.get_rect().width / 2, 70))
    screen.blit(message1, (screenX / 2 - message1.get_rect().width / 2, 130))
    screen.blit(message2, (screenX / 2 - message2.get_rect().width / 2, 165))

    # Display data titles
    line1_Y = 230
    line2_Y = 250
    column = captionFont.render("Starting", True, WHITE)
    screen.blit(column, ((170 - column.get_rect().width) / 2, line1_Y))
    column = captionFont.render("ants", True, WHITE)
    screen.blit(column, ((170 - column.get_rect().width) / 2, line2_Y))

    column = captionFont.render("Ending", True, WHITE)
    screen.blit(column, ((390 - column.get_rect().width) / 2, line1_Y))
    column = captionFont.render("ants", True, WHITE)
    screen.blit(column, ((390 - column.get_rect().width) / 2, line2_Y))

    column = captionFont.render("Food", True, WHITE)
    screen.blit(column, ((610 - column.get_rect().width) / 2, line1_Y))
    column = captionFont.render("found", True, WHITE)
    screen.blit(column, ((610 - column.get_rect().width) / 2, line2_Y))

    column = captionFont.render("Time", True, WHITE)
    screen.blit(column, ((830 - column.get_rect().width) / 2, line1_Y))
    column = captionFont.render("taken", True, WHITE)
    screen.blit(column, ((830 - column.get_rect().width) / 2, line2_Y))

    # Display data
    startAnts = font.render(str(dataToDelete[1]), True, WHITE)
    endAnts = font.render(str(dataToDelete[2]), True, WHITE)
    food = font.render(str(dataToDelete[3]), True, WHITE)

    min = str(dataToDelete[4] // 60)
    sec = str(dataToDelete[4] % 60)
    if len(sec) == 1:
        sec = "0" + sec
    timeTaken = font.render(min + ":" + sec, True, WHITE)

    dataY = 275
    screen.blit(startAnts, ((170 - startAnts.get_rect().width) / 2, dataY))
    screen.blit(endAnts, ((390 - endAnts.get_rect().width) / 2, dataY))
    screen.blit(food, ((610 - food.get_rect().width) / 2, dataY))
    screen.blit(timeTaken, ((830 - timeTaken.get_rect().width) / 2, dataY))

    # Wait for user to take action
    pg.display.update()

    buttonPosY = 350
    buttonSize = (140, 50)
    delete = Button((300, buttonPosY), buttonSize, "Delete", ORANGE_OFF, ORANGE_ON, delete=True)
    cancel = Button((60, buttonPosY), buttonSize, "Cancel", ORANGE_OFF, ORANGE_ON)
    delete.drawOffButton()
    cancel.drawOffButton()

    run = True
    while run:
        for event in pg.event.get():
            if not delete.mouseOn(event):
                statement = "DELETE FROM statistics WHERE id = " + str(dataToDelete[0])
                c.execute(statement)
                db.commit()
                run = False
            elif not cancel.mouseOn(event):
                run = False


def drawBoxes():
    screen.fill(MENU_ORANGE)
    # Numbers are taken from local variables in viewData()
    pg.draw.rect(screen, ORANGE_OFF, (30, 70, 440, 390))
    pg.draw.rect(screen, ORANGE_ON, (30, 70, 440, 390), 4)
    pg.draw.line(screen, ORANGE_ON, (30, 130), (470, 130), 4)
    pg.draw.line(screen, ORANGE_ON, (140, 70), (140, 460), 4)
    pg.draw.line(screen, ORANGE_ON, (250, 70), (250, 460), 4)
    pg.draw.line(screen, ORANGE_ON, (360, 70), (360, 460), 4)


loadImgs()
mainMenu()
db.close()
pg.quit()
