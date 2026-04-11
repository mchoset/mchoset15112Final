'test2'

import win32com.client
import os
import time

def importAndExtrudeNewPart(dxfPath, thicknessMm):
    if not os.path.exists(dxfPath):
        print(f"Error: The file does not exist at {dxfPath}")
        return

    scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    macroPath = os.path.join(scriptDirectory, "tempImportMacro.swb")

    thicknessMeters = thicknessMm / 1000.0

    # The macro now selects the feature object directly in memory
    macroCode = f"""Dim swApp As SldWorks.SldWorks
Dim importData As SldWorks.ImportDxfDwgData
Dim newDoc As SldWorks.ModelDoc2
Dim myFeature As Object
Dim feat As SldWorks.Feature
Dim targetSketch As SldWorks.Feature
Dim errors As Long

Sub main()
    Set swApp = Application.SldWorks
    Set importData = swApp.GetImportFileData("{dxfPath}")
    
    importData.ImportMethod("") = 2
    
    errors = 0
    Set newDoc = swApp.LoadFile4("{dxfPath}", "", importData, errors)
    
    If Not newDoc Is Nothing Then
        newDoc.ClearSelection2 True
        
        ' Scan the feature tree to find the imported sketch object
        Set feat = newDoc.FirstFeature
        Do While Not feat Is Nothing
            If feat.GetTypeName2() = "ProfileFeature" Then
                ' Save the exact object reference
                Set targetSketch = feat
            End If
            Set feat = feat.GetNextFeature
        Loop
        
        If Not targetSketch Is Nothing Then
            ' Directly select the object in memory (False = don't append to current selection, 0 = default mark)
            targetSketch.Select2 False, 0
            
            ' Extrude the selected sketch
            Set myFeature = newDoc.FeatureManager.FeatureExtrusion3(True, False, False, 0, 0, {thicknessMeters}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False)
            
            newDoc.ViewZoomtofit2
        End If
    End If
End Sub
"""
    
    with open(macroPath, "w") as f:
        f.write(macroCode)

    try:
        swApp = win32com.client.GetActiveObject("SldWorks.Application")
    except Exception:
        swApp = win32com.client.Dispatch("SldWorks.Application")
    
    swApp.Visible = True
    
    try:
        swApp.RunMacro(macroPath, "tempImportMacro", "main")
        print(f"Successfully imported and extruded {dxfPath} to {thicknessMm}mm")
    except Exception as e:
        print(f"Macro execution failed: {e}")

    time.sleep(2) 
    if os.path.exists(macroPath):
        try:
            os.remove(macroPath)
        except Exception as e:
            print(f"Note: Could not delete temporary macro file. {e}")

def importAndExtrudeExisitingPart(dxfPath, thicknessMm):
    if not os.path.exists(dxfPath):
        print(f"Error: file missing at {dxfPath}")
        return

    scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    macroPath = os.path.join(scriptDirectory, "tempDxfInsert.swb")

    thicknessMeters = thicknessMm / 1000.0

    macroCode = f"""Dim swApp As SldWorks.SldWorks
Dim swModel As SldWorks.ModelDoc2
Dim swFeatMgr As SldWorks.FeatureManager
Dim currentFeat As SldWorks.Feature
Dim swFeat As SldWorks.Feature
Dim myFeature As Object
Dim bSelected As Boolean

Sub main()
    Set swApp = Application.SldWorks
    Set swModel = swApp.ActiveDoc
    
    If swModel Is Nothing Then
        MsgBox "No active document found. Please open a part first."
        Exit Sub
    End If
    
    swModel.ClearSelection2 True
    bSelected = False
    
    ' Find the first Reference Plane to place the sketch on
    Set currentFeat = swModel.FirstFeature
    Do While Not currentFeat Is Nothing
        If currentFeat.GetTypeName2() = "RefPlane" Then
            bSelected = currentFeat.Select2(False, 0)
            Exit Do
        End If
        Set currentFeat = currentFeat.GetNextFeature()
    Loop
    
    If Not bSelected Then
        bSelected = swModel.Extension.SelectByID2("Front Plane", "PLANE", 0, 0, 0, False, 0, Nothing, 0)
    End If
    
    Set swFeatMgr = swModel.FeatureManager
    
    ' Passing Nothing explicitly binds the import to the active document and plane
    Set swFeat = swFeatMgr.InsertDwgOrDxfFile2("{dxfPath}", Nothing)
    
    If Not swFeat Is Nothing Then
        swModel.ClearSelection2 True
        swFeat.Select2 False, 0
        
        ' Extrude the newly inserted sketch
        Set myFeature = swFeatMgr.FeatureExtrusion3(True, False, False, 0, 0, {thicknessMeters}, 0, False, False, False, False, 0, 0, False, False, False, False, True, True, True, 0, 0, False)
        swModel.ViewZoomtofit2
    End If
End Sub
"""
    
    with open(macroPath, "w") as f:
        f.write(macroCode)

    try:
        swApp = win32com.client.GetActiveObject("SldWorks.Application")
    except Exception:
        swApp = win32com.client.Dispatch("SldWorks.Application")
    
    swApp.Visible = True
    
    try:
        swApp.RunMacro(macroPath, "tempDxfInsert", "main")
        print(f"Imported and extruded {dxfPath} inside the active document")
    except Exception as e:
        print(f"Failed to run macro: {e}")

    time.sleep(2) 
    if os.path.exists(macroPath):
        try:
            os.remove(macroPath)
        except Exception:
            pass

def getPath(fileName):
    scriptDirectory = os.path.dirname(os.path.abspath(__file__))
    targetFileName = fileName
    dxfFile = os.path.join(scriptDirectory, targetFileName)

    return dxfFile

def deleteFile(path):
    if os.path.exists(path):
        try:
            os.remove(path)
            print(f"Successfully deleted DXF file at: {path}")
        except Exception as e:
            print(f"Note: Could not delete DXF file. {e}")