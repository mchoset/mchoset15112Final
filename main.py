from cmu_graphics import *
import ezdxf
import math
import exportDrive
import printDrive
import os

'''
*** All AI use was with Gemini 3.1 Pro***
'''

# Equations given by AI that define the shape of the cycloidal disk.
# I will exempt these equations given by AI
'''
--------------------------------------------------------------------------------
Inputs that define cycloidal drive geometry
R = radius of circle on which the stationary pins form [mm]
Np = num of stationary pins [unitless]
e = eccentricity (offset of the cyclodial disk's center from input shaft center) [mm]
r = radius of external pins [mm]
t = input parameter [radians]
------------------------------------------------------------------------------
Equations that define cyloidal drive geometry
phaseAngle = math.atan2(math.sin((1 - N)*t),((R/(e*N))-math.cos((1 N)*t)))
x(t) = R*math.cos(t) - r*math.cos(t + phaseAngle) - e*math.cos(N*t)
y(t) = -R*math.sin(t) + r*math.sin(t + phaseAngle) + e*math.sin(N*t))
--------------------------------------------------------------------------------
'''

def getRadiusEndpoints(cx, cy, r, theta):
    return (cx + r*math.cos(math.radians(theta)), 
            cy - r*math.sin(math.radians(theta)))

def distance(x0, y0, x1, y1):
    return math.sqrt((x1-x0)**2 + (y1-y0)**2)

def generateXYPoints(app, parameterStart, parameterEnd, numPoints):
    stepSize = (parameterEnd - parameterStart)/(numPoints - 1)
    R = app.R
    e = app.e
    Np = app.Np
    r = app.r
    coordinates = []
    for i in range(numPoints):
        t = parameterStart + i*stepSize
        phaseAngle = (math.atan2(math.sin((1 - Np)*t),
                                 ((R/(e*Np))-math.cos((1 - Np)*t))))
        x = ((R*math.cos(t) - r*math.cos(t + phaseAngle) - 
              e*math.cos(Np*t)))
        y = ((-R*math.sin(t) + r*math.sin(t + phaseAngle) + 
             e*math.sin(Np*t)))
        coordinates.append((x, y))
    return coordinates

def onAppStart(app):
    app.width = 1200
    app.height = 800

    app.R = 40.0
    app.Np = 8
    app.e = 1.5
    app.r = 4.5
    app.camShaftRadius = 5.0
    app.numOutputShafts = 4
    app.outputShaftDistFromCenter = 20.0
    app.outputShaftRadius = 4.0

    app.scalar = app.height/(app.R*5)
    app.stepsPerSecond = 30
    app.paused = False

    app.diskAngleDeg = 0
    app.shaftAngleDeg = 0

    app.verticalGearShift = app.height*13/24

    app.scaledEccentricity = app.e*app.scalar
    app.currentDiskCenterX, app.currentDiskCenterY = (getRadiusEndpoints
                                                      (app.width/2, 
                                                       app.verticalGearShift, 
                                                       app.scaledEccentricity, 
                                                       -app.shaftAngleDeg))

    app.tolerance = 2.5*10**-4
    app.extrustionThickness = 0.01

    app.resolution = 500
    app.centeredGearPoints = generateXYPoints(app, 0, 2*math.pi, app.resolution)
    
    app.fullScreen = False

# ----------------------------------DRAWING-------------------------------------

def redrawAll(app):
    drawGear(app)
    drawGearHoles(app)
    drawInputShaft(app)
    drawOutputShafts(app)
    drawExternalPins(app)
    drawLabels(app)
    drawButtons(app)
    drawArrows(app)

def drawInputBox(x, y, width, height, label, value, keybind):
    drawLabel(label, x, y - 10, align='left', size=14, bold=True)
    drawLabel(f'Key: {keybind}', x + width, y - 10, align='right', size=12, 
              fill='gray', bold=True)
    drawRect(x, y, width, height, fill='white', border='lightgray', borderWidth=2)
    drawLabel(value, x + 10, y + height/2, align='left', size=16)

def drawLabels(app):
    '''AI made the boxes look cleaner. It added in the margin idea/space btwn boxes outlining the buttons'''
    marginSize = 20 # AI
    boxWidth = (app.width - marginSize*5)/4 # AI
    boxHeight = 40
    startY0 = 40
    startY1 = 120
    drawInputBox(marginSize, startY0, boxWidth, boxHeight, # AI
                 'Number of Pins', f'{app.Np}' + f'   (Gear Ratio {app.Np-1}:1)', 
                 'Up/Down')
    drawInputBox(marginSize*2 + boxWidth, startY0, boxWidth, boxHeight, # AI
                 'Pin Circle Radius', f'{app.R} mm', 'Left/Right')
    drawInputBox(marginSize*3 + boxWidth*2, startY0, boxWidth, boxHeight, # AI
                 'Eccentricity', f'{app.e} mm', 'W/S')
    drawInputBox(marginSize*4 + boxWidth*3, startY0, boxWidth, boxHeight, # AI
                 'External Pin Radius', f'{app.r} mm', 'Q/A')
    drawInputBox(marginSize, startY1, boxWidth, boxHeight, # AI
                 'Cam Shaft Radius', f'{app.camShaftRadius} mm', 'I/K')
    drawInputBox(marginSize*2 + boxWidth, startY1, boxWidth, boxHeight, # AI
                 'Output Pins', f'{app.numOutputShafts}', 'T/G')
    drawInputBox(marginSize*3 + boxWidth*2, startY1, boxWidth, boxHeight, # AI
                 'Output Pin Radius', f'{app.outputShaftRadius} mm', 'Y/H')
    drawInputBox(marginSize*4 + boxWidth*3, startY1, boxWidth, boxHeight, # AI
                 'Output Pin Circle Radius', 
                 f'{app.outputShaftDistFromCenter} mm', 'U/J')
    pausedStatus = 'unpause' if app.paused else 'pause'
    drawLabel(f'Press P to {pausedStatus}', app.width/2, 
              startY1 + boxHeight + 25, size=16, bold=True)

def drawButtons(app):
    buttonWidth = app.width*0.4
    buttonHeight = app.height*0.1
    buttonCenterY = app.height*0.92
    button1CenterX = app.width*0.28
    button2CenterX = app.width*0.72
    drawRect(button1CenterX, buttonCenterY, buttonWidth, buttonHeight, fill='blue', 
             border='black', borderWidth=5, align='center')
    drawLabel('Generate DXF', button1CenterX, buttonCenterY, 
              size=app.height*0.04, bold=True, fill='white')
    drawRect(button2CenterX, buttonCenterY, buttonWidth, buttonHeight, fill='red', 
             border='black', borderWidth=5, align='center')
    drawLabel('Export to Sldwrks & 3DP', button2CenterX, buttonCenterY, 
              size=app.height*0.04, bold=True, fill='white')

def drawGear(app):
    adjustedGearPoints = []
    for x, y in app.centeredGearPoints:
        adjustedGearPoints.append((x*app.scalar) + app.currentDiskCenterX)
        adjustedGearPoints.append((y*app.scalar) + app.currentDiskCenterY)
    drawPolygon(*adjustedGearPoints, rotateAngle=app.diskAngleDeg)

def drawGearHoles(app):
    drawCircle(app.currentDiskCenterX, app.currentDiskCenterY, 
               app.camShaftRadius*app.scalar, fill='gray')
    holeRadius = app.outputShaftRadius + app.e
    for i in range(app.numOutputShafts):
        thetaDeg = i*(360/app.numOutputShafts) + app.diskAngleDeg
        cx, cy = getRadiusEndpoints(app.currentDiskCenterX, 
                                    app.currentDiskCenterY, 
                                    app.outputShaftDistFromCenter*app.scalar, 
                                    -thetaDeg)
        drawCircle(cx, cy, holeRadius*app.scalar, fill='white')

def drawInputShaft(app):
    cx = app.width/2
    cy = app.verticalGearShift
    inputShaftRadius = (app.camShaftRadius - app.e)*app.scalar
    drawCircle(cx, cy, inputShaftRadius, fill='darkGray')
    indicatorX, indicatorY = getRadiusEndpoints(cx, cy, inputShaftRadius, 
                                                -app.shaftAngleDeg)
    drawLine(cx, cy, indicatorX, indicatorY, fill='black', lineWidth=2)

def drawOutputShafts(app):
    extPinsCenterX = app.width/2
    extPinsCenterY = app.verticalGearShift
    for i in range(app.numOutputShafts):
        angleDeg = i*(360/app.numOutputShafts) + app.diskAngleDeg
        cx, cy = getRadiusEndpoints(extPinsCenterX, extPinsCenterY, 
                                    app.outputShaftDistFromCenter*app.scalar, 
                                    -angleDeg)
        drawCircle(cx, cy, app.outputShaftRadius*app.scalar, fill='blue')
    
def drawExternalPins(app):
    centerX = app.width/2
    centerY = app.verticalGearShift
    for i in range(app.Np):
        angleDeg = i*(360/app.Np)
        cx, cy = getRadiusEndpoints(centerX, centerY, 
                                    app.R*app.scalar, angleDeg)
        scaledPinRadius = app.r*app.scalar
        drawCircle(cx, cy, scaledPinRadius, fill='green')

def drawUpArrow(cx, cy):
    drawPolygon(cx, cy-5, cx-6, cy+5, cx+6, cy+5, fill='black')

def drawDownArrow(cx, cy):
    drawPolygon(cx, cy+5, cx-6, cy-5, cx+6, cy-5, fill='black')

def drawArrows(app):
    '''AI gave me the code to figure out the center of the triangles'''
    marginSize = 20
    boxWidthidth = (app.width-marginSize*5)/4
    boxHeighteight = 40
    boxYValues = [40, 120]

    for boxY in boxYValues:
        for arrowCol in range(4):
            boxLeftX = marginSize*(arrowCol + 1) + boxWidthidth*arrowCol # AI
            arrowCx = boxLeftX + boxWidthidth - 15 # AI
            upArrowCy = boxY + boxHeighteight/2 - 8 # AI
            downArrowCy = boxY + boxHeighteight/2 + 8 # AI
            drawUpArrow(arrowCx, upArrowCy)
            drawDownArrow(arrowCx, downArrowCy)

# ---------------------------Changing Stuff-------------------------------------
def onStep(app):
    if app.fullScreen == False:
        exportDrive.maximizeWindow()
        app.fullScreen = True
    app.scalar = app.height/(app.R*5)
    app.verticalGearShift = app.height*13/24
    if not app.paused:
        takeStep(app)

def takeStep(app):
    dTheta = 5
    app.shaftAngleDeg += dTheta
    app.diskAngleDeg -= dTheta/(app.Np-1)
    app.scaledEccentricity = app.e*app.scalar
    app.currentDiskCenterX, app.currentDiskCenterY = (getRadiusEndpoints
                                                      (app.width/2, 
                                                       app.verticalGearShift, 
                                                       app.scaledEccentricity, 
                                                       -app.shaftAngleDeg))

def onMousePress(app, mouseX, mouseY):
    checkDxfButton(app, mouseX, mouseY)
    checkArrows(app, mouseX, mouseY)

def checkArrows(app, mouseX, mouseY):
    '''
    AI Wrote the code for the hitboxes of the arrows
    '''
    # Starts here
    marginSize = 20
    boxWidthidth = (app.width - marginSize*5)/4
    boxHeighteight = 40
    startY0 = 40
    startY1 = 120
    hitboxSize = 10

    col0ArrowCx = marginSize*1 + boxWidthidth - 15
    col1ArrowCx = marginSize*2 + boxWidthidth*1 + boxWidthidth - 15
    col2ArrowCx = marginSize*3 + boxWidthidth*2 + boxWidthidth - 15
    col3ArrowCx = marginSize*4 + boxWidthidth*3 + boxWidthidth - 15

    row0UpArrowCy = startY0 + boxHeighteight/2 - 8
    row0DownArrowCy = startY0 + boxHeighteight/2 + 8
    
    row1UpCy = startY1 + boxHeighteight/2 - 8
    row1DownCy = startY1 + boxHeighteight/2 + 8
    # Ends Here

    if (col0ArrowCx - hitboxSize <= mouseX <= col0ArrowCx + hitboxSize and 
        row0UpArrowCy - hitboxSize <= mouseY <= row0UpArrowCy + hitboxSize):
        onKeyPress(app, 'up')
        return
    elif (col0ArrowCx - hitboxSize <= mouseX <= col0ArrowCx + hitboxSize and 
        row0DownArrowCy - hitboxSize <= mouseY <= row0DownArrowCy + hitboxSize):
        onKeyPress(app, 'down')
        return

    elif (col1ArrowCx - hitboxSize <= mouseX <= col1ArrowCx + hitboxSize and 
        row0UpArrowCy - hitboxSize <= mouseY <= row0UpArrowCy + hitboxSize):
        onKeyPress(app, 'right')
        return
    elif (col1ArrowCx - hitboxSize <= mouseX <= col1ArrowCx + hitboxSize and 
        row0DownArrowCy - hitboxSize <= mouseY <= row0DownArrowCy + hitboxSize):
        onKeyPress(app, 'left')
        return

    elif (col2ArrowCx - hitboxSize <= mouseX <= col2ArrowCx + hitboxSize and 
        row0UpArrowCy - hitboxSize <= mouseY <= row0UpArrowCy + hitboxSize):
        onKeyPress(app, 'w')
        return
    elif (col2ArrowCx - hitboxSize <= mouseX <= col2ArrowCx + hitboxSize and 
        row0DownArrowCy - hitboxSize <= mouseY <= row0DownArrowCy + hitboxSize):
        onKeyPress(app, 's')
        return

    elif (col3ArrowCx - hitboxSize <= mouseX <= col3ArrowCx + hitboxSize and 
        row0UpArrowCy - hitboxSize <= mouseY <= row0UpArrowCy + hitboxSize):
        onKeyPress(app, 'q')
        return
    elif (col3ArrowCx - hitboxSize <= mouseX <= col3ArrowCx + hitboxSize and 
        row0DownArrowCy - hitboxSize <= mouseY <= row0DownArrowCy + hitboxSize):
        onKeyPress(app, 'a')
        return

    elif (col0ArrowCx - hitboxSize <= mouseX <= col0ArrowCx + hitboxSize and 
        row1UpCy - hitboxSize <= mouseY <= row1UpCy + hitboxSize):
        onKeyPress(app, 'i')
        return
    elif (col0ArrowCx - hitboxSize <= mouseX <= col0ArrowCx + hitboxSize and 
        row1DownCy - hitboxSize <= mouseY <= row1DownCy + hitboxSize):
        onKeyPress(app, 'k')
        return

    elif (col1ArrowCx - hitboxSize <= mouseX <= col1ArrowCx + hitboxSize and 
        row1UpCy - hitboxSize <= mouseY <= row1UpCy + hitboxSize):
        onKeyPress(app, 't')
        return
    elif (col1ArrowCx - hitboxSize <= mouseX <= col1ArrowCx + hitboxSize and 
        row1DownCy - hitboxSize <= mouseY <= row1DownCy + hitboxSize):
        onKeyPress(app, 'g')
        return

    elif (col2ArrowCx - hitboxSize <= mouseX <= col2ArrowCx + hitboxSize and 
        row1UpCy - hitboxSize <= mouseY <= row1UpCy + hitboxSize):
        onKeyPress(app, 'y')
        return
    elif (col2ArrowCx - hitboxSize <= mouseX <= col2ArrowCx + hitboxSize and 
        row1DownCy - hitboxSize <= mouseY <= row1DownCy + hitboxSize):
        onKeyPress(app, 'h')
        return

    elif (col3ArrowCx - hitboxSize <= mouseX <= col3ArrowCx + hitboxSize and 
        row1UpCy - hitboxSize <= mouseY <= row1UpCy + hitboxSize):
        onKeyPress(app, 'u')
        return
    elif (col3ArrowCx - hitboxSize <= mouseX <= col3ArrowCx + hitboxSize and 
        row1DownCy - hitboxSize <= mouseY <= row1DownCy + hitboxSize):
        onKeyPress(app, 'j')
        return

def checkDxfButton(app, mouseX, mouseY):
    buttonWidth = app.width*0.4
    buttonHeight = app.height*0.1
    buttonCenterY = app.height*0.92
    button1CenterX = app.width*0.28
    button2CenterX = app.width*0.72
    if ((button1CenterX - buttonWidth/2 < mouseX < button1CenterX + buttonWidth/2) and 
        (buttonCenterY - buttonHeight/2 < mouseY < buttonCenterY + buttonHeight/2)):
        generateDxf(app)
    if ((button2CenterX - buttonWidth/2 < mouseX < button2CenterX + buttonWidth/2) and 
        (buttonCenterY - buttonHeight/2 < mouseY < buttonCenterY + buttonHeight/2)):
        exportDriveTo3DP(app)

def onKeyPress(app, key):
    if key in ['p', 'P']:
        app.paused = not app.paused
        return

    NpOld = app.Np
    ROld = app.R
    eOld = app.e
    rOld = app.r
    camShaftRadiusOld = app.camShaftRadius
    numOutputShaftsOld = app.numOutputShafts
    outputShaftRadiusOld = app.outputShaftRadius
    outputShaftDistFromCenterOld = app.outputShaftDistFromCenter

    if key == 'up':
        app.Np += 1
    elif key == 'down' and app.Np > 3:
        app.Np -= 1
    elif key == 'right':
        app.R += 0.5
    elif key == 'left':
        app.R -= 0.5
    elif key in ['w', 'W']:
        app.e += 0.5
    elif key in ['s', 'S']:
        app.e -= 0.5
    elif key in ['q', 'Q']:
        app.r += 0.5
    elif key in ['a', 'A']:
        app.r -= 0.5
    elif key in ['i', 'I']:
        app.camShaftRadius += 0.5
    elif key in ['k', 'K']:
        app.camShaftRadius -= 0.5
    elif key in ['t', 'T']:
        app.numOutputShafts += 1
    elif key in ['g', 'G']:
        app.numOutputShafts -= 1
    elif key in ['y', 'Y']:
        app.outputShaftRadius += 0.5
    elif key in ['h', 'H']:
        app.outputShaftRadius -= 0.5
    elif key in ['u', 'U']:
        app.outputShaftDistFromCenter += 0.5
    elif key in ['j', 'J']:
        app.outputShaftDistFromCenter -= 0.5
    else:
        return
    if checkValidParameters(app):
        app.diskAngleDeg = 0
        app.shaftAngleDeg = 0
        app.scalar = app.height/(app.R*5)
        app.scaledEccentricity = app.e*app.scalar
        app.currentDiskCenterX, app.currentDiskCenterY = (getRadiusEndpoints
                                                          (app.width/2, 
                                                           app.verticalGearShift, 
                                                           app.scaledEccentricity, 
                                                           -app.shaftAngleDeg))
        app.centeredGearPoints = generateXYPoints(app, 0, 2*math.pi, app.resolution)
    else:
        app.Np = NpOld
        app.R = ROld
        app.e = eOld
        app.r = rOld
        app.camShaftRadius = camShaftRadiusOld
        app.numOutputShafts = numOutputShaftsOld
        app.outputShaftRadius = outputShaftRadiusOld
        app.outputShaftDistFromCenter = outputShaftDistFromCenterOld

def checkValidParameters(app):
    Np = app.Np
    R = app.R
    e = app.e
    r = app.r
    camRadius = app.camShaftRadius
    outputR = app.outputShaftRadius
    outputDist = app.outputShaftDistFromCenter
    numOutput = app.numOutputShafts
    outputHoleRadius = outputR + e
    minThickness = 2

# ----------------- These conditions were found by AI --------------------------
# I will exempt lines 442-462 (all the conditions the gear must meet)
    distBetweenOutputHoleAndEdge = 2*outputDist*math.sin(math.pi/numOutput)
    if R < e*(Np ** 2):
        minRho = ((R - e*Np)**2)/(e*(Np**2) - R) 
    else:
        minRho = ((R + e*Np)**2)/(R + e*(Np**2))
    conditions = {
        R > 0,
        e > 0,
        r > 0,
        Np > 3,
        camRadius > 0,
        camRadius < R/3,
        outputR  > 0.5,
        outputDist > camRadius + outputR,
        numOutput > 1,
        outputDist > camRadius + outputHoleRadius + minThickness,
        distBetweenOutputHoleAndEdge > 2*outputHoleRadius + minThickness,
        outputDist + outputHoleRadius < R - r - e - minThickness,
        R > e*Np,
        r < minRho
    }
# ------------------------------------------------------------------------------
    for condition in conditions:
        if condition == False: return False
    return True


# ----------------------DXF AND SLDWRKS STUFF-----------------------------------

'''
These commands from now to the end of the file and the variables they were assigned to were written by AI:
ezdxf.new()
doc.modelspace()
msp.add_lwpolyline
msp.add_circle
doc.saveas(fileName)

The process for drawing a line/circle in a dxf file is almost the exactly the
as doing it in cmu_graphics. AI gave the syntax to create/edit the dxf files
using the ezdxf module

These commands from the os module and the variables they were assigned to were written by AI:
os.remove(os.path.join(os.path.dirname(__file__), fileName))
'''

def exportDriveTo3DP(app):
    importGearToSldwrks(app)
    importStationaryPinsToSldwrks(app)
    importOutputPinsToSldwrks(app)
    importInputShaftToSldwrks(app)
    exportDrive.finishSolidworksModeling(app)
    printDrive.exportSolidBodies()
    printDrive.generateGcode()


def importGearToSldwrks(app):
    e = app.e
    outR = app.outputShaftRadius
    outDist = app.outputShaftDistFromCenter
    numOut = app.numOutputShafts
    holeRadius = outR + e
    camRadius = app.camShaftRadius

    coordinates = [((x + e)/1000, (y/1000)) for x, y in app.centeredGearPoints]
    doc = ezdxf.new() # AI
    msp = doc.modelspace() # AI
    msp.add_lwpolyline(coordinates, close=True) # AI
    for i in range(numOut): # output holes
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(e/1000, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=holeRadius/1000 + app.tolerance) # AI
    msp.add_circle((e/1000, 0), radius=camRadius/1000 + app.tolerance/2) # AI
    fileName = 'cycloidalGearForSldwrksTemp.dxf'
    doc.saveas(fileName) # AI

    flipDirection = False
    merge = False
    exportDrive.importAndCreateNewPart(fileName, app.extrustionThickness, 
                                       flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName)) # AI

def importStationaryPinsToSldwrks(app):
    R = app.R
    Np = app.Np
    r = app.r

    doc = ezdxf.new() # AI
    msp = doc.modelspace() # AI
    for i in range(Np): # ext pins
        thetaDeg = i*(360/Np)
        cx, cy = getRadiusEndpoints(0, 0, R/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=r/1000 - app.tolerance) # AI
    fileName = 'extPinsTemp.dxf'
    doc.saveas(fileName) # AI
    
    flipDirection = False
    merge = False
    exportDrive.importToExistingPart(fileName, app.extrustionThickness*1.25, 
                                     flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName)) # AI

def importOutputPinsToSldwrks(app):
    outR = app.outputShaftRadius
    outDist = app.outputShaftDistFromCenter
    numOut = app.numOutputShafts

    doc = ezdxf.new() # AI
    msp = doc.modelspace() # AI
    for i in range(numOut): # output pins
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(0, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=outR/1000) # AI
    fileName = 'outputPinsTemp.dxf'
    doc.saveas(fileName) # AI
    
    flipDirection = False
    merge = False
    exportDrive.importToExistingPart(fileName, app.extrustionThickness*1.3, 
                                     flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName)) # AI

def importInputShaftToSldwrks(app):
    e = app.e
    camRadius = app.camShaftRadius
    inputShaftRadius = camRadius - e

    doc = ezdxf.new() # AI
    msp = doc.modelspace() # AI
    msp.add_circle((e/1000, 0), radius=camRadius/1000)# AI
    fileName = 'inputShaftTemp1.dxf'
    doc.saveas(fileName) # AI
    
    flipDirection = False
    merge = False
    exportDrive.importToExistingPart(fileName, app.extrustionThickness, 
                                     flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName)) # AI

    # ------------ Cam Shaft -> Input Shaft ---------------
    doc = ezdxf.new() # AI
    msp = doc.modelspace() # AI

    msp.add_circle((0, 0), radius=(inputShaftRadius/1000)*0.75) # AI
    fileName = 'inputShaftTemp2.dxf'
    doc.saveas(fileName) # AI
    
    flipDirection = True
    merge = True
    exportDrive.importToExistingPart(fileName, app.extrustionThickness*2, 
                                     flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName)) # AI

def generateDxf(app):
    R = app.R
    Np = app.Np
    r = app.r
    e = app.e
    camRadius = app.camShaftRadius
    outR = app.outputShaftRadius
    outDist = app.outputShaftDistFromCenter
    numOut = app.numOutputShafts
    holeRadius = outR + e
    inputShaftRadius = camRadius - e
    
    coordinates = [((x + e)/1000, (y/1000)) for x, y in app.centeredGearPoints]
    doc = ezdxf.new() # AI
    msp = doc.modelspace() # AI
    msp.add_lwpolyline(coordinates, close=True) # AI
    msp.add_circle((e/1000, 0), radius=camRadius/1000) # AI
    msp.add_circle((0, 0), radius=inputShaftRadius/1000) # AI
    for i in range(numOut):
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(e/1000, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=holeRadius/1000) # AI
    for i in range(numOut):
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(0, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=outR/1000) # AI
    for i in range(Np):
        thetaDeg = i*(360/Np)
        cx, cy = getRadiusEndpoints(0, 0, R/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=r/1000) # AI

    doc.saveas('cycloidalDrive.dxf') # AI

runApp()