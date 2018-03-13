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

 Dim bsTrough 'The trough object'
 SolCallback(13) = "bsTrough.SolOut"

 Sub Table1_init()
  
  With Controller
       .GameName=cGameName
       If Err Then MsgBox "Can't start Game" & cGameName & vbNewLine & Err.Description : Exit Sub
       .SplashInfoLine="****GAMENAME******" & vbNewLine & "P-ROC by *********"
       .HandleKeyboard=0
       .ShowTitle=0
       .ShowDMDOnly=1
       .ShowFrame=0
       .HandleMechanics=0
       '.Hidden=1
       '.SetDisplayPosition 1600, 1600, GetPlayerHWnd
       On Error Resume Next
       .Run GetPlayerHWnd
       If Err Then MsgBox Err.Description
    End With
 
    On Error Goto 0

  VpmInit me

    ' Trough    
    Set bsTrough=New cvpmBallStack
    bsTrough.InitSw 0,84,83,82,81,0,0,0
    bsTrough.InitKick BallRelease, 80, 6
    bsTrough.InitEntrySnd "Solenoid", "Solenoid"
    bsTrough.InitExitSnd "ballrel", "Solenoid"
    bsTrough.Balls=4

    ' Main Timer init
    PinMAMETimer.Interval=PinMAMEInterval
    PinMAMETimer.Enabled=1

    vpmCreateEvents AllSwitches

    'Initialize plungers
    Plunger.PullBack
    'KickBack.PullBack

 End Sub

'################
'# Flippers
'###############

SolCallback(sLRFlipper) = "SolRFlipper"
SolCallback(sLLFlipper) = "SolLFlipper"

Sub SolLFlipper(Enabled)    
    If Enabled Then
        PlaySound "flipUpSound", 0, 1, -0.1, 0.25
        LeftFlipper.RotateToEnd
    Else        
        PlaySound "flipDownSound", 0, 1, -0.1, 0.25
        LeftFlipper.RotateToStart
    End If
End Sub

Sub SolRFlipper(Enabled)
    Dim tmp, tmp2
    If Enabled Then
        PlaySound "flipUpSound", 0, 1, 0.1, 0.25
        RightFlipper.RotateToEnd
    Else        
        PlaySound "flipDownSound", 0, 1, 0.1, 0.25
        RightFlipper.RotateToStart
    End If
End Sub

'###############
' GAME SWITCHES
'###############

' shooter_lane hit 
Sub sw41_Hit():Controller.Switch(41) = 1:End Sub
Sub sw41_UnHit():Controller.Switch(41) = 0:End Sub

Sub Drain_Hit() 
  bsTrough.AddBall Me  
End Sub

'**********
' Keys
'**********
 Sub Table1_KeyDown(ByVal Keycode)    

  If keycode = PlungerKey Then
    Plunger.PullBack
    PlaySound "plungerpull",0,1,AudioPan(Plunger),0.25,0,0,1,AudioFade(Plunger)
  End If

  If vpmKeyDown(keycode) Then Exit Sub
 End Sub

 Sub Table1_KeyUp(ByVal Keycode)

  If keycode = PlungerKey Then
    Plunger.Fire
    PlaySound "plunger",0,1,AudioPan(Plunger),0.25,0,0,1,AudioFade(Plunger)
  End If

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





'*********************************************************************
'                 Positional Sound Playback Functions
'*********************************************************************

' Play a sound, depending on the X,Y position of the table element (especially cool for surround speaker setups, otherwise stereo panning only)
' parameters (defaults): loopcount (1), volume (1), randompitch (0), pitch (0), useexisting (0), restart (1))
' Note that this will not work (currently) for walls/slingshots as these do not feature a simple, single X,Y position
Sub PlayXYSound(soundname, tableobj, loopcount, volume, randompitch, pitch, useexisting, restart)
	PlaySound soundname, loopcount, volume, AudioPan(tableobj), randompitch, pitch, useexisting, restart, AudioFade(tableobj)
End Sub

' Similar subroutines that are less complicated to use (e.g. simply use standard parameters for the PlaySound call)
Sub PlaySoundAt(soundname, tableobj)
    PlaySound soundname, 1, 1, AudioPan(tableobj), 0,0,0, 1, AudioFade(tableobj)
End Sub

Sub PlaySoundAtBall(soundname)
    PlaySoundAt soundname, ActiveBall
End Sub


'*********************************************************************
'                     Supporting Ball & Sound Functions
'*********************************************************************

Function AudioFade(tableobj) ' Fades between front and back of the table (for surround systems or 2x2 speakers, etc), depending on the Y position on the table. "table1" is the name of the table
	Dim tmp
    tmp = tableobj.y * 2 / table1.height-1
    If tmp > 0 Then
		AudioFade = Csng(tmp ^10)
    Else
        AudioFade = Csng(-((- tmp) ^10) )
    End If
End Function

Function AudioPan(tableobj) ' Calculates the pan for a tableobj based on the X position on the table. "table1" is the name of the table
    Dim tmp
    tmp = tableobj.x * 2 / table1.width-1
    If tmp > 0 Then
        AudioPan = Csng(tmp ^10)
    Else
        AudioPan = Csng(-((- tmp) ^10) )
    End If
End Function

Function Vol(ball) ' Calculates the Volume of the sound based on the ball speed
    Vol = Csng(BallVel(ball) ^2 / 2000)
End Function

Function Pitch(ball) ' Calculates the pitch of the sound based on the ball speed
    Pitch = BallVel(ball) * 20
End Function

Function BallVel(ball) 'Calculates the ball speed
    BallVel = INT(SQR((ball.VelX ^2) + (ball.VelY ^2) ) )
End Function


'*****************************************
'   rothbauerw's Manual Ball Control
'*****************************************

Dim BCup, BCdown, BCleft, BCright
Dim ControlBallInPlay, ControlActiveBall
Dim BCvel, BCyveloffset, BCboostmulti, BCboost

BCboost = 1				'Do Not Change - default setting
BCvel = 4				'Controls the speed of the ball movement
BCyveloffset = -0.01 	'Offsets the force of gravity to keep the ball from drifting vertically on the table, should be negative
BCboostmulti = 3		'Boost multiplier to ball veloctiy (toggled with the B key) 

ControlBallInPlay = false

Sub StartBallControl_Hit()
	Set ControlActiveBall = ActiveBall
	ControlBallInPlay = true
End Sub

Sub StopBallControl_Hit()
	ControlBallInPlay = false
End Sub	

Sub BallControlTimer_Timer()
	If EnableBallControl and ControlBallInPlay then
		If BCright = 1 Then
			ControlActiveBall.velx =  BCvel*BCboost
		ElseIf BCleft = 1 Then
			ControlActiveBall.velx = -BCvel*BCboost
		Else
			ControlActiveBall.velx = 0
		End If

		If BCup = 1 Then
			ControlActiveBall.vely = -BCvel*BCboost
		ElseIf BCdown = 1 Then
			ControlActiveBall.vely =  BCvel*BCboost
		Else
			ControlActiveBall.vely = bcyveloffset
		End If
	End If
End Sub


'*****************************************
'      JP's VP10 Rolling Sounds
'*****************************************

Const tnob = 5 ' total number of balls
ReDim rolling(tnob)
InitRolling

Sub InitRolling
    Dim i
    For i = 0 to tnob
        rolling(i) = False
    Next
End Sub

Sub RollingTimer_Timer()
    Dim BOT, b
    BOT = GetBalls

	' stop the sound of deleted balls
    For b = UBound(BOT) + 1 to tnob
        rolling(b) = False
        StopSound("fx_ballrolling" & b)
    Next

	' exit the sub if no balls on the table
    If UBound(BOT) = -1 Then Exit Sub

	' play the rolling sound for each ball
    For b = 0 to UBound(BOT)
        If BallVel(BOT(b) ) > 1 AND BOT(b).z < 30 Then
            rolling(b) = True
            PlaySound("fx_ballrolling" & b), -1, Vol(BOT(b)), AudioPan(BOT(b)), 0, Pitch(BOT(b)), 1, 0, AudioFade(BOT(b))
        Else
            If rolling(b) = True Then
                StopSound("fx_ballrolling" & b)
                rolling(b) = False
            End If
        End If
    Next
End Sub

'**********************
' Ball Collision Sound
'**********************

Sub OnBallBallCollision(ball1, ball2, velocity)
	PlaySound("fx_collide"), 0, Csng(velocity) ^2 / 2000, AudioPan(ball1), 0, Pitch(ball1), 0, 0, AudioFade(ball1)
End Sub


'*****************************************
'	ninuzzu's	FLIPPER SHADOWS
'*****************************************

sub FlipperTimer_Timer()
	FlipperLSh.RotZ = LeftFlipper.currentangle
	FlipperRSh.RotZ = RightFlipper.currentangle

End Sub

'*****************************************
'	ninuzzu's	BALL SHADOW
'*****************************************
Dim BallShadow
BallShadow = Array (BallShadow1,BallShadow2,BallShadow3,BallShadow4,BallShadow5)

Sub BallShadowUpdate_timer()
    Dim BOT, b
    BOT = GetBalls
    ' hide shadow of deleted balls
    If UBound(BOT)<(tnob-1) Then
        For b = (UBound(BOT) + 1) to (tnob-1)
            BallShadow(b).visible = 0
        Next
    End If
    ' exit the Sub if no balls on the table
    If UBound(BOT) = -1 Then Exit Sub
    ' render the shadow for each ball
    For b = 0 to UBound(BOT)
        If BOT(b).X < Table1.Width/2 Then
            BallShadow(b).X = ((BOT(b).X) - (Ballsize/6) + ((BOT(b).X - (Table1.Width/2))/7)) + 6
        Else
            BallShadow(b).X = ((BOT(b).X) + (Ballsize/6) + ((BOT(b).X - (Table1.Width/2))/7)) - 6
        End If
        ballShadow(b).Y = BOT(b).Y + 12
        If BOT(b).Z > 20 Then
            BallShadow(b).visible = 1
        Else
            BallShadow(b).visible = 0
        End If
    Next
End Sub



'************************************
' What you need to add to your table
'************************************

' a timer called RollingTimer. With a fast interval, like 10
' one collision sound, in this script is called fx_collide
' as many sound files as max number of balls, with names ending with 0, 1, 2, 3, etc
' for ex. as used in this script: fx_ballrolling0, fx_ballrolling1, fx_ballrolling2, fx_ballrolling3, etc


'******************************************
' Explanation of the rolling sound routine
'******************************************

' sounds are played based on the ball speed and position

' the routine checks first for deleted balls and stops the rolling sound.

' The For loop goes through all the balls on the table and checks for the ball speed and 
' if the ball is on the table (height lower than 30) then then it plays the sound
' otherwise the sound is stopped, like when the ball has stopped or is on a ramp or flying.

' The sound is played using the VOL, AUDIOPAN, AUDIOFADE and PITCH functions, so the volume and pitch of the sound
' will change according to the ball speed, and the AUDIOPAN & AUDIOFADE functions will change the stereo position
' according to the position of the ball on the table.


'**************************************
' Explanation of the collision routine
'**************************************

' The collision is built in VP.
' You only need to add a Sub OnBallBallCollision(ball1, ball2, velocity) and when two balls collide they 
' will call this routine. What you add in the sub is up to you. As an example is a simple Playsound with volume and paning
' depending of the speed of the collision.


Sub Pins_Hit (idx)
	PlaySound "pinhit_low", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 0, 0, AudioFade(ActiveBall)
End Sub

Sub Targets_Hit (idx)
	PlaySound "target", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 0, 0, AudioFade(ActiveBall)
End Sub

Sub Metals_Thin_Hit (idx)
	PlaySound "metalhit_thin", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
End Sub

Sub Metals_Medium_Hit (idx)
	PlaySound "metalhit_medium", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
End Sub

Sub Metals2_Hit (idx)
	PlaySound "metalhit2", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
End Sub

Sub Gates_Hit (idx)
	PlaySound "gate4", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
End Sub

Sub Spinner_Spin
	PlaySound "fx_spinner", 0, .25, AudioPan(Spinner), 0.25, 0, 0, 1, AudioFade(Spinner)
End Sub

Sub Rubbers_Hit(idx)
 	dim finalspeed
  	finalspeed=SQR(activeball.velx * activeball.velx + activeball.vely * activeball.vely)
 	If finalspeed > 20 then 
		PlaySound "fx_rubber2", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
	End if
	If finalspeed >= 6 AND finalspeed <= 20 then
 		RandomSoundRubber()
 	End If
End Sub

Sub Posts_Hit(idx)
 	dim finalspeed
  	finalspeed=SQR(activeball.velx * activeball.velx + activeball.vely * activeball.vely)
 	If finalspeed > 16 then 
		PlaySound "fx_rubber2", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
	End if
	If finalspeed >= 6 AND finalspeed <= 16 then
 		RandomSoundRubber()
 	End If
End Sub

Sub RandomSoundRubber()
	Select Case Int(Rnd*3)+1
		Case 1 : PlaySound "rubber_hit_1", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
		Case 2 : PlaySound "rubber_hit_2", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
		Case 3 : PlaySound "rubber_hit_3", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
	End Select
End Sub

Sub LeftFlipper_Collide(parm)
 	RandomSoundFlipper()
End Sub

Sub RightFlipper_Collide(parm)
 	RandomSoundFlipper()
End Sub

Sub RandomSoundFlipper()
	Select Case Int(Rnd*3)+1
		Case 1 : PlaySound "flip_hit_1", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
		Case 2 : PlaySound "flip_hit_2", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
		Case 3 : PlaySound "flip_hit_3", 0, Vol(ActiveBall), AudioPan(ActiveBall), 0, Pitch(ActiveBall), 1, 0, AudioFade(ActiveBall)
	End Select
End Sub