from win32com.client import *
import pythoncom
import os
import pyautogui
import pygetwindow
import time

def createNewPart():
    swApp = Dispatch("SldWorks.Application")
    swApp.Visible = True
    templatePath = swApp.GetUserPreferenceStringValue(8)
    swModel = swApp.NewDocument(templatePath, 0, 0, 0)
    swModel.Extension

def selectTopPlane():
    swApp = Dispatch( "SldWorks.Application" )
    swModel = swApp.ActiveDoc        
    swExt = swModel.Extension
    nullObject = VARIANT(pythoncom.VT_DISPATCH, None)
    swExt.SelectByID2("Top Plane", "PLANE", 0.0, 0.0, 0.0, False, 0, nullObject, 0)

def importDxf(dxfFileName):
    swWindows = pygetwindow.getWindowsWithTitle('SOLIDWORKS')
    swWindow = swWindows[0]
    
    if swWindow.isMinimized:
        swWindow.restore()
        
    try:
        swWindow.activate()
    except Exception:
        pyautogui.press('alt')
        swWindow.activate()
    
    time.sleep(2) 
    
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    dxfPath = os.path.join(scriptDir, dxfFileName)
    if dxfPath[0] not in ['c', 'C']:
        dxfPath = 'C' + dxfPath
    else:
        print(dxfPath)

    pyautogui.press('f12')
    
    time.sleep(2) 
    
    pyautogui.write(dxfPath)
    pyautogui.press('enter')
    pyautogui.press('enter', presses=3, interval=5)

def importDxfToSldwrks(dxfFileName):
    createNewPart()
    selectTopPlane()
    importDxf(dxfFileName)
    

importDxfToSldwrks('cycloidalDrive.dxf')