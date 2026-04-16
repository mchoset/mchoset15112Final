import win32com.client
import os
import pythoncom

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
            model.SaveAs3(savePath, 0, 1)
            body.HideBody(True)

    for body in bodies:
        body.HideBody(False)