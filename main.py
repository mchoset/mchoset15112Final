from cmu_graphics import *
import ezdxf
import math
import importDxf
import os

'''
need to create tolerances within the dxf import
S'''
# Equations
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

def generateXYPoints(app, tStart, tEnd, numPoints): # WILL RESULT IN GEAR CENTERED AT ORIGIN
    stepSize = (tEnd - tStart)/(numPoints - 1)
    R = app.R
    e = app.e
    Np = app.Np
    r = app.r

    coordinates = []
    for i in range(numPoints):
        t = tStart + i*stepSize
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
    app.stepsPerSecond = 60
    app.paused = False

    app.diskAngleDeg = 0
    app.shaftAngleDeg = 0

    app.verticalGearShift = app.height * 1/2

    app.scaledEccentricity = app.e*app.scalar
    app.currentDiskCenterX, app.currentDiskCenterY = (getRadiusEndpoints
                                                      (app.width/2, 
                                                       app.verticalGearShift, 
                                                       app.scaledEccentricity, 
                                                       -app.shaftAngleDeg))

    app.tolerance = 2.5*10**-5

    app.resolution = 500
    app.centeredGearPoints = generateXYPoints(app, 0, 2*math.pi, app.resolution)

def redrawAll(app):
    drawGear(app)
    drawGearHoles(app)
    drawInputShaft(app)
    drawOutputShafts(app)
    drawExternalPins(app)
    drawLabels(app)
    drawButton(app)
    drawArrows(app)

def drawInputBox(x, y, width, height, labelText, valueText, keybind):
    drawLabel(labelText, x, y - 10, align='left', size=14, bold=True)
    drawLabel(f'Key: {keybind}', x + width, y - 10, align='right', size=12, fill='dimgray', bold=True)
    drawRect(x, y, width, height, fill='white', border='lightgray', borderWidth=2)
    drawLabel(valueText, x + 10, y + height/2, align='left', size=16)

def drawLabels(app):
    padding = 20
    boxW = (app.width - padding*5)/4
    boxH = 40
    startY1 = 40
    startY2 = 120

    drawInputBox(padding, startY1, boxW, boxH,
                 'Number of Pins', str(app.Np) + f'  (Gear Ratio {app.Np-1}:1)', 'Up/Down')
    drawInputBox(padding*2 + boxW, startY1, boxW, boxH,
                 'Pin Circle Radius', f'{app.R} mm', 'Left/Right')
    drawInputBox(padding*3 + boxW*2, startY1, boxW, boxH,
                 'Eccentricity', f'{app.e} mm', 'W/S')
    drawInputBox(padding*4 + boxW*3, startY1, boxW, boxH,
                 'External Pin Radius', f'{app.r} mm', 'Q/A')
    drawInputBox(padding, startY2, boxW, boxH,
                 'Cam Shaft Radius', f'{app.camShaftRadius} mm', 'I/K')
    drawInputBox(padding*2 + boxW, startY2, boxW, boxH,
                 'Output Pins', str(app.numOutputShafts), 'T/G')
    drawInputBox(padding*3 + boxW*2, startY2, boxW, boxH,
                 'Output Pin Radius', f'{app.outputShaftRadius} mm', 'Y/H')
    drawInputBox(padding*4 + boxW*3, startY2, boxW, boxH,
                 'Output Pin Circle Radius', f'{app.outputShaftDistFromCenter} mm', 'U/J')

    pausedStatus = 'unpause' if app.paused else 'pause'
    drawLabel(f"Press P to {pausedStatus}", app.width/2, startY2 + boxH + 25, size=16, bold=True)

def drawButton(app):
    btnWidth = app.width * 0.4
    btnHeight = app.height * 0.1
    btnCenterY = app.height * 0.92
    
    btn1CenterX = app.width * 0.28
    btn2CenterX = app.width * 0.72

    drawRect(btn1CenterX, btnCenterY, btnWidth, btnHeight, fill='blue', 
             border='black', borderWidth=5, align='center')
    drawLabel('Generate DXF', btn1CenterX, btnCenterY, 
              size=app.height*0.04, bold=True, fill='white')

    drawRect(btn2CenterX, btnCenterY, btnWidth, btnHeight, fill='red', 
             border='black', borderWidth=5, align='center')
    drawLabel('Export to Solidworks', btn2CenterX, btnCenterY, 
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
        thetaDeg = i * (360 / app.numOutputShafts) + app.diskAngleDeg
        cx, cy = getRadiusEndpoints(app.currentDiskCenterX, 
                                    app.currentDiskCenterY, 
                                    app.outputShaftDistFromCenter*app.scalar, 
                                    -thetaDeg)
        drawCircle(cx, cy, holeRadius*app.scalar, fill='white')

def drawInputShaft(app):
    cx = app.width/2
    cy = app.verticalGearShift

    inputShaftRadius = (app.camShaftRadius - app.e) * app.scalar
    drawCircle(cx, cy, inputShaftRadius, fill='darkGray')
    indicatorX, indicatorY = getRadiusEndpoints(cx, cy, inputShaftRadius, 
                                                -app.shaftAngleDeg)
    drawLine(cx, cy, indicatorX, indicatorY, fill='black', lineWidth=2)

def drawOutputShafts(app):
    extPinsCenterX = app.width/2
    extPinsCenterY = app.verticalGearShift
    
    for i in range(app.numOutputShafts):
        angleDeg = i * (360 / app.numOutputShafts) + app.diskAngleDeg
        cx, cy = getRadiusEndpoints(extPinsCenterX, extPinsCenterY, 
                                    app.outputShaftDistFromCenter*app.scalar, 
                                    -angleDeg)
        drawCircle(cx, cy, app.outputShaftRadius*app.scalar, fill='blue')
    
def drawExternalPins(app):
    centerX = app.width/2
    centerY = app.verticalGearShift
    
    for i in range(app.Np):
        angleDeg = i * (360 / app.Np)
        cx, cy = getRadiusEndpoints(centerX, centerY, 
                                    app.R*app.scalar, -angleDeg)
        scaledPinRadius = app.r*app.scalar
        drawCircle(cx, cy, scaledPinRadius, fill='green')

def drawUpArrow(cx, cy):
    drawPolygon(cx, cy - 5, cx - 6, cy + 5, cx + 6, cy + 5, fill='black')

def drawDownArrow(cx, cy):
    drawPolygon(cx, cy + 5, cx - 6, cy - 5, cx + 6, cy - 5, fill='black')

def drawArrows(app):
    padding = 20
    boxWidth = (app.width-padding*5) / 4
    boxHeight = 40
    yValues = [40, 120]

    for rowY in yValues:
        for arrowCol in range(4):
            boxLeftX = padding*(arrowCol + 1) + boxWidth*arrowCol
            arrowCx = boxLeftX + boxWidth - 15
            
            upArrowCy = rowY + boxHeight/2 - 8
            downArrowCy = rowY + boxHeight/2 + 8
            
            drawUpArrow(arrowCx, upArrowCy)
            drawDownArrow(arrowCx, downArrowCy)

def onStep(app):
    app.scalar = app.height/(app.R*5)
    app.verticalGearShift = 7*app.height/12
    if not app.paused:
        takeStep(app)

def takeStep(app):
    stepAmount = 5
    app.shaftAngleDeg += stepAmount
    app.diskAngleDeg -= stepAmount / (app.Np-1)

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
    padding = 20
    boxWidth = (app.width - padding*5) / 4
    boxHeight = 40
    yValues = [40, 120]
    
    keyMap = {
        (0, 0): ('up', 'down'),
        (0, 1): ('right', 'left'),
        (0, 2): ('w', 's'),
        (0, 3): ('q', 'a'),
        (1, 0): ('i', 'k'),
        (1, 1): ('t', 'g'),
        (1, 2): ('y', 'h'),
        (1, 3): ('u', 'j')
    }

    for rowIndex in range(len(yValues)):
        rowY = yValues[rowIndex]
        for arrowCol in range(4):
            boxLeftX = padding*(arrowCol + 1) + boxWidth*arrowCol
            arrowCx = boxLeftX + boxWidth - 15
            
            upArrowCy = rowY + boxHeight/2 - 8
            downArrowCy = rowY + boxHeight/2 + 8
            
            hitboxSize = 10
            
            if (arrowCx - hitboxSize <= mouseX <= arrowCx + hitboxSize and 
                upArrowCy - hitboxSize <= mouseY <= upArrowCy + hitboxSize):
                simulatedKey = keyMap[(rowIndex, arrowCol)][0]
                onKeyPress(app, simulatedKey)
                return
                
            if (arrowCx - hitboxSize <= mouseX <= arrowCx + hitboxSize and 
                downArrowCy - hitboxSize <= mouseY <= downArrowCy + hitboxSize):
                simulatedKey = keyMap[(rowIndex, arrowCol)][1]
                onKeyPress(app, simulatedKey)
                return

def checkDxfButton(app, mouseX, mouseY):
    btnWidth = app.width * 0.4
    btnHeight = app.height * 0.1
    btnCenterY = app.height * 0.92
    
    btn1CenterX = app.width * 0.28
    btn2CenterX = app.width * 0.72

    if ((btn1CenterX - btnWidth/2 < mouseX < btn1CenterX + btnWidth/2) and 
        (btnCenterY - btnHeight/2 < mouseY < btnCenterY + btnHeight/2)):
        generateDxf(app)

    if ((btn2CenterX - btnWidth/2 < mouseX < btn2CenterX + btnWidth/2) and 
        (btnCenterY - btnHeight/2 < mouseY < btnCenterY + btnHeight/2)):
        importDriveToSldwrks(app)

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
        app.scalar = app.height / (app.R*5)
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
        print('INVALID')

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

    minThickness = 2 # mm

    if R <= 0 or e <= 0 or r <= 0 or Np < 3 or camRadius <= 0 or camRadius >= R/3:
        return False

    if outputR <= 0.5 or outputDist <= camRadius + outputR or numOutput < 1:
        return False

    if outputDist <= camRadius + outputHoleRadius + minThickness:
        return False

    distBetweenOutputHoleAndEdge = 2*outputDist*math.sin(math.pi/numOutput)
    if distBetweenOutputHoleAndEdge <= 2*outputHoleRadius + minThickness:
        return False

    if outputDist + outputHoleRadius >= R - r - e - minThickness:
        return False

    if R <= e*Np: # gear can not self-intersect
        return False
    
    if R < e*(Np ** 2):
        minRho = ((R - e*Np)**2)/(e*(Np**2) - R) 
    else:
        minRho = ((R + e*Np)**2)/(R + e*(Np**2)) # don't know the scenario this would happen but gemini said it could
    # rho is curvature of a certian part of the disk measured by radius
        
    return r < minRho

def importDriveToSldwrks(app):
    importGearToSldwrks(app)
    importExtPinsToSldwrks(app)
    importOutputPinsToSldwrks(app)
    importInputShaftToSldwrks(app)

def importGearToSldwrks(app):
    e = app.e
    outR = app.outputShaftRadius
    outDist = app.outputShaftDistFromCenter
    numOut = app.numOutputShafts
    holeRadius = outR + e
    camRadius = app.camShaftRadius

    coordinates = [((x + e)/1000, (y/1000)) for x, y in app.centeredGearPoints]
    doc = ezdxf.new()
    msp = doc.modelspace()
    msp.add_lwpolyline(coordinates, close=True)

    for i in range(numOut): # output holes
        thetaDeg = i * (360 / numOut)
        cx, cy = getRadiusEndpoints(e/1000, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=holeRadius/1000 + app.tolerance)

    msp.add_circle((e/1000, 0), radius=camRadius/1000 + app.tolerance)

    fileName = 'cycloidalGearForSldwrksTemp.dxf'
    doc.saveas(fileName)

    # ------------ IMPORTING TO SOLIDWORKS --------------
    importDxf.importAndCreateNewPart(fileName)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))


def importExtPinsToSldwrks(app):
    R = app.R
    Np = app.Np
    r = app.r

    doc = ezdxf.new()
    msp = doc.modelspace()

    for i in range(Np): # ext pins
        thetaDeg = i * (360 / Np)
        cx, cy = getRadiusEndpoints(0, 0, R/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=r/1000 - app.tolerance)

    fileName = 'extPinsTemp.dxf'
    doc.saveas(fileName)
    # ------------ IMPORTING TO SOLIDWORKS --------------
    importDxf.importToExistingPart(fileName)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))


def importOutputPinsToSldwrks(app):
    outR = app.outputShaftRadius
    outDist = app.outputShaftDistFromCenter
    numOut = app.numOutputShafts

    doc = ezdxf.new()
    msp = doc.modelspace()

    for i in range(numOut): # output pins
        thetaDeg = i * (360 / numOut)
        cx, cy = getRadiusEndpoints(0, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=outR/1000)

    fileName = 'outputPinsTemp.dxf'
    doc.saveas(fileName)
    # ------------ IMPORTING TO SOLIDWORKS --------------
    importDxf.importToExistingPart(fileName)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))

def importInputShaftToSldwrks(app):
    e = app.e
    camRadius = app.camShaftRadius
    inputShaftRadius = camRadius - e

    doc = ezdxf.new()
    msp = doc.modelspace()

    msp.add_circle((0, 0), radius=inputShaftRadius/1000)
    msp.add_circle((e/1000, 0), radius=camRadius/1000)

    fileName = 'inputShaftTemp.dxf'
    doc.saveas(fileName)
    # ------------ IMPORTING TO SOLIDWORKS --------------
    importDxf.importToExistingPart(fileName)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))

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

    doc = ezdxf.new()
    msp = doc.modelspace()
    
    msp.add_lwpolyline(coordinates, close=True)
    
    msp.add_circle((e/1000, 0), radius=camRadius/1000)
    msp.add_circle((0, 0), radius=inputShaftRadius/1000)

    for i in range(numOut): # output holes
        thetaDeg = i * (360 / numOut)
        cx, cy = getRadiusEndpoints(e/1000, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=holeRadius/1000)

    for i in range(numOut): # output pins
        thetaDeg = i * (360 / numOut)
        cx, cy = getRadiusEndpoints(0, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=outR/1000)

    for i in range(Np): # ext pins
        thetaDeg = i * (360 / Np)
        cx, cy = getRadiusEndpoints(0, 0, R/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=r/1000)

    doc.saveas('cycloidalDrive.dxf')

runApp()