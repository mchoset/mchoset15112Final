import win32com.client
import pythoncom
import os

def createNewPart():
    swApp = win32com.client.Dispatch('SldWorks.Application')
    swApp.Visible = True
    templatePath = swApp.GetUserPreferenceStringValue(8)
    swModel = swApp.NewDocument(templatePath, 0, 0, 0)
    swModel.Extension

def selectTopPlane():
    swApp = win32com.client.Dispatch('SldWorks.Application')
    swModel = swApp.ActiveDoc        
    swExt = swModel.Extension
    nullObject = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    swExt.SelectByID2('Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, nullObject, 0)

def importDxf(dxfFileName):
    swApp = win32com.client.Dispatch('SldWorks.Application')
    swModel = swApp.ActiveDoc
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    dxfPath = os.path.join(scriptDir, dxfFileName)
    swModel.FeatureManager.InsertDwgOrDxfFile(dxfPath)

def createSketch():
    swApp = win32com.client.Dispatch('SldWorks.Application')
    swModel = swApp.ActiveDoc
    swExt = swModel.Extension
    nullObject = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)

    swModel.ClearSelection2(True)
    swExt.SelectByID2('Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, nullObject, 0)
    swModel.SketchManager.InsertSketch(True)
    swModel.ClearSelection2(True)
    swExt.SelectByID2('Sketch1', 'SKETCH', 0.0, 0.0, 0.0, False, 0, nullObject, 0)
    swModel.SketchManager.SketchUseEdge3(False, False)
    swModel.ClearSelection2(True)
    swModel.SketchManager.InsertSketch(True)

    swExt.SelectByID2('Sketch1', "SKETCH", 0.0, 0.0, 0.0, False, 0, nullObject, 0)
    swModel.BlankSketch()

def importAndCreateNewPart(dxfFileName):
    createNewPart()
    selectTopPlane()
    importDxf(dxfFileName)
    
def importToExistingPart(dxfFileName):
    selectTopPlane()
    importDxf(dxfFileName)