import win32com.client
import pythoncom
import os
import math
import pyautogui
import time

'''
*** All AI use was with Gemini 3.1 Pro***
'''

'''
AI gave me these modules, functions, and functions that can occur from the 
variables assigned to these functions, however I wrote the general logic for 
all the functions, and can explain it in my oral assesment

A better way to describe my AI use in this file would be I used AI as a way
to generate documentation for using the Solidworks API via python (there is 
minimal online). Using that documentation I was able to build the code that 
creates the cyclodial drive in solidworks.

----------------------------------- AI CODE -----------------------------------
win32com.client: win32com.client.Dispatch('SldWorks.Application') <-- creates COM object
    --> AI gave me all the methods I can use w/ the COM object


os: os.getcwd(), os.path.join(scriptDirectory, 'fileName') <-- for file handling

*AI wrote for me every line that pythoncom occurs in
-------------------------------------------------------------------------------

I do not know how many of the functions/modules work on a low level, but I can 
explain the step-by-step proccess used to generate the disk within solidworks.
'''

def minimizeWindow():
    pyautogui.hotkey('win', 'down')

def maximizeWindow():
    pyautogui.hotkey('win', 'up')

def getRadiusEndpoints(cx, cy, r, theta):
    return (cx + r*math.cos(math.radians(theta)), 
            cy - r*math.sin(math.radians(theta)))

def createNewPart():
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swApp.Visible = True # AI
    templatePath = swApp.GetUserPreferenceStringValue(8) # AI
    swModel = swApp.NewDocument(templatePath, 0, 0, 0)
    swModel.Extension # AI
    minimizeWindow()
    goFullscreen()
    
def goFullscreen():
    time.sleep(5)
    for n in range(20, 0, -1):
        windows = pyautogui.getWindowsWithTitle(f'Part{n}')
        if windows != []:
            windows[0].activate()
        pyautogui.hotkey('win', 'up')

def selectTopPlane():
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    swExt = swModel.Extension # AI
    swExt.SelectByID2('Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, 
                      pythoncom.Nothing, 0)

def importDxf(dxfFileName):
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    dxfPath = os.path.join(scriptDir, dxfFileName)
    swModel.FeatureManager.InsertDwgOrDxfFile(dxfPath)

def extrudeSketch(depth, flipDirection, merge):
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    swModel.FeatureManager.FeatureExtrusion3( # AI
        True,           # 1: Single direction
        False,          # 2: Flip side to cut
        flipDirection,  # 3: Direction
        0,              # 4: Termination type end 1
        0,              # 5: Termination type end 2
        depth,          # 6: Depth end 1
        0.0,            # 7: Depth end 2
        False,          # 8: Draft end 1
        False,          # 9: Draft end 2
        False,          # 10: Draft inward end 1
        False,          # 11: Draft inward end 2
        0.0,            # 12: Draft angle end 1
        0.0,            # 13: Draft angle end 2
        False,          # 14: Offset reverse end 1
        False,          # 15: Offset reverse end 2
        False,          # 16: Translate surface end 1
        False,          # 17: Translate surface end 2 <--- This was missing
        merge,          # 18: Merge result
        True,           # 19: Use feature scope
        True,           # 20: Use auto-select
        0,              # 21: Start condition (T0)
        0.0,            # 22: Start offset 
        False           # 23: Flip start offset 
    )

def createOffsetPlaneFromTop(distance, flipDirection):
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    swExt = swModel.Extension # AI
    swExt.SelectByID2('Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, pythoncom.Nothing, 0)
    swModel.FeatureManager.InsertRefPlane(flipDirection, distance, 0, 0.0, 0, 0.0)

def importAndCreateNewPart(dxfFileName, depth, flipExtrudeDirection, merge):
    createNewPart()
    selectTopPlane()
    importDxf(dxfFileName)
    extrudeSketch(depth, flipExtrudeDirection, merge)
    
def importToExistingPart(dxfFileName, depth, flipExtrudeDirection, merge):
    selectTopPlane()
    importDxf(dxfFileName)
    extrudeSketch(depth, flipExtrudeDirection, merge)

def finishSolidworksModeling(app):
    makeDriveHousing(app)
    makeOutput(app)

def makeDriveHousing(app):
    selectTopPlane()
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    swModel.InsertSketch2(True)
    swSketchManager = swModel.SketchManager # AI
    
    innerRadius = app.R/1000
    outerRadius = app.R/1000 + app.r/1000
    swSketchManager.CreateCircleByRadius(0.0, 0.0, 0.0, innerRadius)
    swSketchManager.CreateCircleByRadius(0.0, 0.0, 0.0, outerRadius)
    flipDirection = False
    merge = True
    extrudeSketch(app.extrustionThickness*1.25, flipDirection, merge)

    selectTopPlane()
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    swModel.InsertSketch2(True)
    swSketchManager = swModel.SketchManager
    innerRadius = app.camShaftRadius/1000 + app.e/1000 + app.tolerance
    outerRadius = app.R/1000 + app.r/1000
    swSketchManager.CreateCircleByRadius(0.0, 0.0, 0.0, innerRadius)
    swSketchManager.CreateCircleByRadius(0.0, 0.0, 0.0, outerRadius)
    flipDirection = True
    merge = False
    extrudeSketch(app.extrustionThickness/4, flipDirection, merge) 

    combineHousingBodies()

def makeOutput(app):
    flipDirection = 8 # False
    createOffsetPlaneFromTop(app.extrustionThickness*1.3, flipDirection)
    swApp = win32com.client.Dispatch('SldWorks.Application') # AI
    swModel = swApp.ActiveDoc
    swExt = swModel.Extension # AI
    swExt.SelectByID2('Plane6', 'PLANE', 0.0, 0.0, 0.0, False, 0, 
                      pythoncom.Nothing, 0)
    swModel.InsertSketch2(True)
    swSketchManager = swModel.SketchManager
    swSketchManager.CreateCircleByRadius(0.0, 0.0, 0.0, 
                                         (app.outputShaftDistFromCenter+
                                          app.outputShaftRadius)/1000)
    flipDirection = False
    merge = True
    extrudeSketch(app.extrustionThickness/4, flipDirection, merge)

def combineHousingBodies():
    swApp = win32com.client.Dispatch('SldWorks.Application')
    scriptDir = os.getcwd()
    macroPath = os.path.join(scriptDir, 'combineMacro.swp')
    errorCode = win32com.client.VARIANT(pythoncom.VT_BYREF|pythoncom.VT_I4, 0) # AI
    swApp.RunMacro2(macroPath, 'combineMacro1', 'main', 0, errorCode) # AI