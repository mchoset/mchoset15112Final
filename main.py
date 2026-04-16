from cmu_graphics import *
import ezdxf
import math
import exportDrive
import printDrive
import os

'''
todo's: merge correct housing bodies
'''

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

# ----------------------------------DRAWING-------------------------------------

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
    marginSize = 20
    boxW = (app.width - marginSize*5)/4
    boxH = 40
    startY0 = 40
    startY1 = 120

    drawInputBox(marginSize, startY0, boxW, boxH,
                 'Number of Pins', str(app.Np) + f'   (Gear Ratio {app.Np-1}:1)', 'Up/Down')
    drawInputBox(marginSize*2 + boxW, startY0, boxW, boxH,
                 'Pin Circle Radius', f'{app.R} mm', 'Left/Right')
    drawInputBox(marginSize*3 + boxW*2, startY0, boxW, boxH,
                 'Eccentricity', f'{app.e} mm', 'W/S')
    drawInputBox(marginSize*4 + boxW*3, startY0, boxW, boxH,
                 'External Pin Radius', f'{app.r} mm', 'Q/A')
    drawInputBox(marginSize, startY1, boxW, boxH,
                 'Cam Shaft Radius', f'{app.camShaftRadius} mm', 'I/K')
    drawInputBox(marginSize*2 + boxW, startY1, boxW, boxH,
                 'Output Pins', str(app.numOutputShafts), 'T/G')
    drawInputBox(marginSize*3 + boxW*2, startY1, boxW, boxH,
                 'Output Pin Radius', f'{app.outputShaftRadius} mm', 'Y/H')
    drawInputBox(marginSize*4 + boxW*3, startY1, boxW, boxH,
                 'Output Pin Circle Radius', f'{app.outputShaftDistFromCenter} mm', 'U/J')

    pausedStatus = 'unpause' if app.paused else 'pause'
    drawLabel(f"Press P to {pausedStatus}", app.width/2, startY1 + boxH + 25, size=16, bold=True)

def drawButton(app):
    btnWidth = app.width*0.4
    btnHeight = app.height*0.1
    btnCenterY = app.height*0.92
    
    btn1CenterX = app.width*0.28
    btn2CenterX = app.width*0.72

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
                                    app.R*app.scalar, -angleDeg)
        scaledPinRadius = app.r*app.scalar
        drawCircle(cx, cy, scaledPinRadius, fill='green')

def drawUpArrow(cx, cy):
    drawPolygon(cx, cy - 5, cx - 6, cy + 5, cx + 6, cy + 5, fill='black')

def drawDownArrow(cx, cy):
    drawPolygon(cx, cy + 5, cx - 6, cy - 5, cx + 6, cy - 5, fill='black')

def drawArrows(app):
    marginSize = 20
    boxWidth = (app.width-marginSize*5)/4
    boxHeight = 40
    yValues = [40, 120]

    for rowY in yValues:
        for arrowCol in range(4):
            boxLeftX = marginSize*(arrowCol + 1) + boxWidth*arrowCol
            arrowCx = boxLeftX + boxWidth - 15
            
            upArrowCy = rowY + boxHeight/2 - 8
            downArrowCy = rowY + boxHeight/2 + 8
            
            drawUpArrow(arrowCx, upArrowCy)
            drawDownArrow(arrowCx, downArrowCy)

# ---------------------------Changing Stuff-------------------------------------
def onStep(app):
    app.scalar = app.height/(app.R*5)
    app.verticalGearShift = app.height*13/24
    if not app.paused:
        takeStep(app)

def takeStep(app):
    stepAmount = 5
    app.shaftAngleDeg += stepAmount
    app.diskAngleDeg -= stepAmount/(app.Np-1)

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
    marginSize = 20
    boxWidth = (app.width - marginSize*5)/4
    boxHeight = 40
    startY0 = 40
    startY1 = 120
    hitboxSize = 10

    col0ArrowCx = marginSize*1 + boxWidth - 15
    col1ArrowCx = marginSize*2 + boxWidth*1 + boxWidth - 15
    col2ArrowCx = marginSize*3 + boxWidth*2 + boxWidth - 15
    col3ArrowCx = marginSize*4 + boxWidth*3 + boxWidth - 15

    row0UpArrowCy = startY0 + boxHeight/2 - 8
    row0DownArrowCy = startY0 + boxHeight/2 + 8
    
    row1UpCy = startY1 + boxHeight/2 - 8
    row1DownCy = startY1 + boxHeight/2 + 8

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
    btnWidth = app.width*0.4
    btnHeight = app.height*0.1
    btnCenterY = app.height*0.92
    
    btn1CenterX = app.width*0.28
    btn2CenterX = app.width*0.72

    if ((btn1CenterX - btnWidth/2 < mouseX < btn1CenterX + btnWidth/2) and 
        (btnCenterY - btnHeight/2 < mouseY < btnCenterY + btnHeight/2)):
        generateDxf(app)

    if ((btn2CenterX - btnWidth/2 < mouseX < btn2CenterX + btnWidth/2) and 
        (btnCenterY - btnHeight/2 < mouseY < btnCenterY + btnHeight/2)):
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
    minThickness = 2

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

    for condition in conditions:
        if condition == False: return False
    return True

# ----------------------DXF AND SLDWRKS STUFF-----------------------------------

def exportDriveTo3DP(app):
    importGearToSldwrks(app)
    importStationaryPinsToSldwrks(app)
    importOutputPinsToSldwrks(app)
    importInputShaftToSldwrks(app)
    exportDrive.finishSolidworksModeling(app)
    printDrive.exportSolidBodies()


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
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(e/1000, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=holeRadius/1000 + app.tolerance)

    msp.add_circle((e/1000, 0), radius=camRadius/1000 + app.tolerance)

    fileName = 'cycloidalGearForSldwrksTemp.dxf'
    doc.saveas(fileName)


    flipDirection = False
    merge = False
    exportDrive.importAndCreateNewPart(fileName, app.extrustionThickness, flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))

def importStationaryPinsToSldwrks(app):
    R = app.R
    Np = app.Np
    r = app.r

    doc = ezdxf.new()
    msp = doc.modelspace()

    for i in range(Np): # ext pins
        thetaDeg = i*(360/Np)
        cx, cy = getRadiusEndpoints(0, 0, R/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=r/1000 - app.tolerance)

    fileName = 'extPinsTemp.dxf'
    doc.saveas(fileName)
    
    flipDirection = False
    merge = False
    exportDrive.importToExistingPart(fileName, app.extrustionThickness*1.25, flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))

def importOutputPinsToSldwrks(app):
    outR = app.outputShaftRadius
    outDist = app.outputShaftDistFromCenter
    numOut = app.numOutputShafts

    doc = ezdxf.new()
    msp = doc.modelspace()

    for i in range(numOut): # output pins
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(0, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=outR/1000)

    fileName = 'outputPinsTemp.dxf'
    doc.saveas(fileName)
    
    flipDirection = False
    merge = False
    exportDrive.importToExistingPart(fileName, app.extrustionThickness*1.5, flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))

def importInputShaftToSldwrks(app):
    e = app.e
    camRadius = app.camShaftRadius
    inputShaftRadius = camRadius - e

    doc = ezdxf.new()
    msp = doc.modelspace()

    msp.add_circle((e/1000, 0), radius=camRadius/1000)

    fileName = 'inputShaftTemp1.dxf'
    doc.saveas(fileName)
    
    flipDirection = False
    merge = False
    exportDrive.importToExistingPart(fileName, app.extrustionThickness, flipDirection, merge)
    os.remove(os.path.join(os.path.dirname(__file__), fileName))

    # ------------ Cam Shaft -> Input Shaft ---------------
    doc = ezdxf.new()
    msp = doc.modelspace()

    msp.add_circle((0, 0), radius=(inputShaftRadius/1000)*0.75)

    fileName = 'inputShaftTemp2.dxf'
    doc.saveas(fileName)
    
    flipDirection = True
    merge = True
    exportDrive.importToExistingPart(fileName, app.extrustionThickness*2, flipDirection, merge)
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

    for i in range(numOut):
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(e/1000, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=holeRadius/1000)

    for i in range(numOut):
        thetaDeg = i*(360/numOut)
        cx, cy = getRadiusEndpoints(0, 0, outDist/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=outR/1000)

    for i in range(Np):
        thetaDeg = i*(360/Np)
        cx, cy = getRadiusEndpoints(0, 0, R/1000, -thetaDeg)
        msp.add_circle((cx, cy), radius=r/1000)

    doc.saveas('cycloidalDrive.dxf')

runApp()