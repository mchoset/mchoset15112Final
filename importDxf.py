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
    comNoneEquivalent = win32com.client.VARIANT(pythoncom.VT_DISPATCH, None)
    swExt.SelectByID2('Top Plane', 'PLANE', 0.0, 0.0, 0.0, False, 0, comNoneEquivalent, 0)

def importDxf(dxfFileName):
    swApp = win32com.client.Dispatch('SldWorks.Application')
    swModel = swApp.ActiveDoc
    scriptDir = os.path.dirname(os.path.abspath(__file__))
    dxfPath = os.path.join(scriptDir, dxfFileName)
    swModel.FeatureManager.InsertDwgOrDxfFile(dxfPath)

def extrudeSkecth(depth):
    swApp = win32com.client.Dispatch('SldWorks.Application')
    swModel = swApp.ActiveDoc
    swModel.FeatureManager.FeatureExtrusion3(
        True,   # Single direction
        False,  # Flip direction
        False,  # Direction
        0,      # Termination type (0 for Blind)
        0,      # Termination type
        depth,   # Depth in meters
        0.0,    # Depth for second direction
        False,  # Draft
        False,  # Draft
        False,  # Draft
        False,  # Draft
        0, 0,   # Draft angles
        False,  # Offset
        False,  # Offset
        False,  # Translate surface
        True,  # Merge result
        True,   # Use material sheet metal
        True,   # Use feature scope
        True,   # Use auto-select
        0, 0,   # Top/Bottom radius
        False   # Check for self-intersection
    )

def importAndCreateNewPart(dxfFileName, depth):
    createNewPart()
    selectTopPlane()
    importDxf(dxfFileName)
    extrudeSkecth(depth)
    
def importToExistingPart(dxfFileName, depth):
    selectTopPlane()
    importDxf(dxfFileName)
    extrudeSkecth(depth)