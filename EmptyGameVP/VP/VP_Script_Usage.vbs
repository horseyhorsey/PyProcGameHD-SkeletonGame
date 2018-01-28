' THIS IS NOT A FULL TABLE SCRIPT.
' IT'S JUST FOR AN EXAMPLE HOW TO READ SETTINGS FROM THE PYPROCGAMES SETTINGS FILE, ASSIGNING LAMPS

Option Explicit
Randomize
Const cGameName="YourRomName"
Const UseSolenoids = 1
Dim B2SController, b2sOn ' For Translites

'Set the current directory because when we read that settings file this script sets it's directory.
Dim WshShell, strCurDir
Set WshShell = CreateObject("WScript.Shell")
strCurDir    = WshShell.CurrentDirectory

'Initialize the script for the current table. Change the script to match the machine type.
LoadVPM "WPC.VBS", 3.55
LoadProcOptions

Sub LoadVPM(VBSfile, VBSver)

    On Error Resume Next
    If ScriptEngineMajorVersion<5 Then MsgBox "VB Script Engine 5.0 or higher required"
    ExecuteGlobal GetTextFile(VBSfile)
    If Err Then MsgBox "Unable to open " & VBSfile & ". Ensure that it is in the same folder as this table. " & vbNewLine & Err.Description
    Set Controller=CreateObject("VPROC.Controller")   
	
	' ARE WE LOADING A TRANSLITE ?
	if Controller.GetSettings("VPTranslite","DirectB2S", cGameName) = 1 Then

		' Set the directory back to where the table was loaded from
		WshShell.CurrentDirectory = strCurDir
		Set B2SController=CreateObject("B2S.Server")
			B2SController.B2SName=cGameName			
			B2SController.Run
		b2sOn = true 
	End If
	On Error Goto 0	
	
End Sub

'**********
' Keys
'**********
 Sub Table1_KeyDown(ByVal Keycode)    
  If vpmKeyDown(keycode) Then Exit Sub
 End Sub

 Sub Table1_KeyUp(ByVal Keycode)
    If vpmKeyUp(keycode) Then Exit Sub
 End Sub

'Sounds
Dim snds_LSling,snds_RSling,snds_flips, flipperVol, snds_bumpers
Dim snds_AutoPlunge,snds_Drain,snds_BallRelease, snds_Scoop, snds_VUK
Dim snds_Saucer, snds_Kicker, snds_DropTargets,snds_DropTargetReset, snds_Targets

'Table Pyhsics Enabled - Table physics are directly loaded into the tables variable
Dim tbl_enabled

'Flipper settings
Dim flp_enabled, flp_strength, flp_friction, flp_mass, flp_elastic, flp_elasticFallOff

Sub LoadProcOptions
' THIS SETS ALL VARIABLES FOR THE SCRIPT FROM USER SETTINGS
' example with sounds. 
' if snds_DropTargetReset Then PlaySound "droptargetreset"

  '############ VPSounds '####################  
  snds_LSling  = Controller.GetSettings ("VPSounds","LSlingshot")
  snds_RSling  = Controller.GetSettings ("VPSounds","RSlingshot")
  snds_flips  = Controller.GetSettings ("VPSounds","Flippers")
  flipperVol = Controller.GetSettings ("VPSounds","FlipperVol")
  snds_bumpers  = Controller.GetSettings ("VPSounds","Bumpers")
  snds_AutoPlunge  = Controller.GetSettings ("VPSounds","AutoPlunger")
  snds_Drain  = Controller.GetSettings ("VPSounds","TroughEnter")
  snds_BallRelease  = Controller.GetSettings ("VPSounds","TroughExit")
  snds_Scoop  = Controller.GetSettings ("VPSounds","Scoop")
  snds_VUK  = Controller.GetSettings ("VPSounds","VUK")
  snds_Saucer  = Controller.GetSettings ("VPSounds","Saucer")
  snds_Kicker  = Controller.GetSettings ("VPSounds","Kicker")
  snds_DropTargets  = Controller.GetSettings ("VPSounds","DropTargets")
  snds_DropTargetReset  = Controller.GetSettings ("VPSounds","DropTargetReset")
  snds_Targets  = Controller.GetSettings ("VPSounds","StandUpTargets")

 '############ VP table physics '####################
  tbl_enabled  = Controller.GetSettings ("VPTable","VPTable Config Enabled")
  If tbl_enabled Then
	Table1.Elasticity = Controller.GetSettings ("VPTable","Elasticity")
	Table1.Friction = Controller.GetSettings ("VPTable","Friction")
	Table1.Gravity = Controller.GetSettings ("VPTable","Gravity")
	Table1.NudgeTime = Controller.GetSettings ("VPTable","NudgeTime")
	Table1.Scatter = Controller.GetSettings ("VPTable","Scatter")	
  End If

 '############ VP Flipper physics '####################
  flp_enabled  = Controller.GetSettings ("VPFlippers","VPFlippers Config Enabled")
  If flp_enabled Then
	flp_strength = Controller.GetSettings ("VPFlippers","Strength")
	flp_elastic = Controller.GetSettings ("VPFlippers","Elasticity")
	flp_elasticFallOff = Controller.GetSettings ("VPFlippers","ElasticityFalloff")
	flp_mass = Controller.GetSettings ("VPFlippers","Mass")	
	flp_friction = Controller.GetSettings ("VPFlippers","Friction")	
	LeftFlipper.Strength = flp_strength
    LeftFlipper.Elasticity = flp_elastic
	LeftFlipper.ElasticityFalloff = flp_elasticFallOff
    LeftFlipper.Mass = flp_mass
	LeftFlipper.Friction = flp_friction
	RightFlipper.Strength = flp_strength
    RightFlipper.Elasticity = flp_elastic
	RightFlipper.ElasticityFalloff = flp_elasticFallOff
    RightFlipper.Mass = flp_mass
	RightFlipper.Friction = flp_friction
  End If    
End Sub

'******************************
' LAMPS & GI - 
' ADD ALL LAMPS TO A COLLECTION CALLED AllLamps
' In the Lamps TimerInterval box enter the lamp number from the machine.yaml
'******************************
Const UseLamps = True
Dim GIon
vpmMapLights AllLamps
Set LampCallback    = GetRef("UpdateMultipleLamps")
Sub UpdateMultipleLamps : End Sub

Set GICallback    = GetRef("UpdateGI")
Sub UpdateGI(giNo, stat)
  Select Case giNo
    Case 0 GI_low(abs(stat))
    Case 1 GI_up(abs(stat))
    Case 2 GI_mid(abs(stat)) ' GI_mid
  End Select
End Sub

Sub SolGI(enabled)
End Sub

Dim lamp
Sub GI_low(enabled)
   For each lamp in GILow
    lamp.State= enabled
   Next
    If enabled Then
		'ColGradeGI.enabled=True:ColGradeGIOff.enabled=False:i=5
		If b2sOn Then B2SController.B2ssetdata 100,1
    Else
		'ColGradeGI.enabled=False:ColGradeGIOff.enabled=True:i=1  
		If b2sOn Then B2SController.B2ssetdata 100,0
    End If

End Sub

Sub GI_up(enabled)
    For each lamp in GITop
    lamp.State=enabled
   Next
    If enabled Then
        If b2sOn Then B2SController.B2ssetdata 101,1
    Else
       If b2sOn Then B2SController.B2ssetdata 101,0
    End If

End Sub

Sub GI_mid(enabled)
   For each lamp in GIMid
       lamp.State=enabled
   Next
    If enabled Then
        If b2sOn Then B2SController.B2ssetdata 102,1
   Else
       If b2sOn Then B2SController.B2ssetdata 102,0
    End If
End Sub