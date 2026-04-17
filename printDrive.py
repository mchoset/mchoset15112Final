import win32com.client
import os
import time
import subprocess
import pyautogui


def exportSolidBodies():
    scriptDirectory = os.getcwd()
    swApp = win32com.client.Dispatch('SldWorks.Application')
    model = swApp.ActiveDoc
    
    bodies = model.GetBodies2(0, False)
    targetNames = ['Boss-Extrude1', 'Boss-Extrude5', 'Combine1', 'Boss-Extrude8']

    for body in bodies:
        body.HideBody(True)

    for body in bodies:
        bodyName = body.Name
        if bodyName in targetNames:
            savePath = rf'{scriptDirectory}\{bodyName}.stl'
            
            body.HideBody(False)
            
            model.ClearSelection2(True)
            model.GraphicsRedraw2()
            time.sleep(1.0)
            
            model.SaveAs3(savePath, 0, 1)
            time.sleep(0.5)
            
            body.HideBody(True)

    for body in bodies:
        body.HideBody(False)

# -----------------------------------------------------------------------------

def generateGcode():
    launchSlicerWithParts()
    arrangePartsAndSlice()

def openBambuStudio(filePaths):
    bambuPath = r'C:\Program Files\Bambu Studio\bambu-studio.exe'
    subprocess.Popen([bambuPath] + filePaths)

def launchSlicerWithParts():
    scriptDirectory = os.getcwd()
    stlFiles = [
        os.path.join(scriptDirectory, 'Boss-Extrude1.stl'),
        os.path.join(scriptDirectory, 'Boss-Extrude5.stl'),
        os.path.join(scriptDirectory, 'Combine1.stl'),
        os.path.join(scriptDirectory, 'Boss-Extrude8.stl')
    ]
    openBambuStudio(stlFiles)

    time.sleep(30)
    pyautogui.press('tab')
    pyautogui.press('enter')
    time.sleep(2)

def arrangePartsAndSlice():
    pyautogui.press('esc')
    time.sleep(1)
    pyautogui.hotkey('shift', 'r')
    time.sleep(1)
    pyautogui.press('a')
    time.sleep(1)
    pyautogui.press('tab')