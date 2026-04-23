import win32com.client
import os
import time
import subprocess
import pyautogui

'''
AI gave me these modules, functions, and functions that can occur from the 
variables assigned to these functions, however I wrote the logic for 
all the functions, and can explain it in my oral assesment

A better way to describe my AI use in this file would be I used AI as a way
to generate documentation for using the Solidworks and Bambu API via python 
(there is minimal online). Using that documentation I was able to build the 
code that creates the cyclodial drive in solidworks.

win32com.client: win32com.client.Dispatch('SldWorks.Application') <-- creates COM object
    --> AI gave me all the methods I can use w/ the COM object

os: os.getcwd(), os.path.join(scriptDirectory, 'fileName') <-- for file handling

subprocess: subprocess.Popen([bambuPath] + filePaths)

I do not know how many of the functions/modules work on a low level, but I can 
explain the step-by-step proccess used to get the solidwokrs file into the 
3d printer slicer software, and from there how the .gcode file is saved
'''

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
    exportGcode()
    cleanupStls()

def openBambuStudio(filePaths):
    bambuPath = r'C:\Program Files\Bambu Studio\bambu-studio.exe'
    subprocess.Popen([bambuPath] + filePaths) #AI

def launchSlicerWithParts():
    scriptDirectory = os.getcwd()
    stlFiles = [
        os.path.join(scriptDirectory, 'Boss-Extrude1.stl'),
        os.path.join(scriptDirectory, 'Boss-Extrude5.stl'),
        os.path.join(scriptDirectory, 'Combine1.stl'),
        os.path.join(scriptDirectory, 'Boss-Extrude8.stl')
    ]
    openBambuStudio(stlFiles) # AI

    time.sleep(40)
    pyautogui.press('esc')
    time.sleep(1)
    pyautogui.press('esc')
    time.sleep(1)

def arrangePartsAndSlice():
    pyautogui.press('esc')
    time.sleep(1)
    pyautogui.hotkey('shift', 'r')
    time.sleep(1)
    pyautogui.press('a')
    time.sleep(1)
    pyautogui.press('tab')

def exportGcode():
    time.sleep(7.5)
    pyautogui.hotkey('ctrl', 'g')
    time.sleep(2)
    scriptDirectory = os.getcwd()
    exportPath = os.path.join(scriptDirectory, 'cycloidalDrive.gcode.3mf')
    pyautogui.write(exportPath)
    time.sleep(1)
    pyautogui.press('enter')

def cleanupStls():
    scriptDirectory = os.getcwd()
    stlFiles = [
        os.path.join(scriptDirectory, 'Boss-Extrude1.stl'),
        os.path.join(scriptDirectory, 'Boss-Extrude5.stl'),
        os.path.join(scriptDirectory, 'Combine1.stl'),
        os.path.join(scriptDirectory, 'Boss-Extrude8.stl')
    ]
    for file in stlFiles:
        os.remove(file)