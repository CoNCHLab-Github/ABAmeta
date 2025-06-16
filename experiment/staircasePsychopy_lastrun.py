#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2025.1.1),
    on June 16, 2025, at 18:16
If you publish work using this script the most relevant publication is:

    Peirce J, Gray JR, Simpson S, MacAskill M, Höchenberger R, Sogo H, Kastman E, Lindeløv JK. (2019) 
        PsychoPy2: Experiments in behavior made easy Behav Res 51: 195. 
        https://doi.org/10.3758/s13428-018-01193-y

"""

# --- Import packages ---
from psychopy import locale_setup
from psychopy import prefs
from psychopy import plugins
plugins.activatePlugins()
prefs.hardware['audioLib'] = 'ptb'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (
    NOT_STARTED, STARTED, PLAYING, PAUSED, STOPPED, STOPPING, FINISHED, PRESSED, 
    RELEASED, FOREVER, priority
)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2025.1.1'
expName = 'staircasePsychopy'  # from the Builder filename that created this script
expVersion = ''
# a list of functions to run when the experiment ends (starts off blank)
runAtExit = []
# information about this experiment
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
    'expVersion|hid': expVersion,
    'psychopyVersion|hid': psychopyVersion,
}

# --- Define some variables which will change depending on pilot mode ---
'''
To run in pilot mode, either use the run/pilot toggle in Builder, Coder and Runner, 
or run the experiment with `--pilot` as an argument. To change what pilot 
#mode does, check out the 'Pilot mode' tab in preferences.
'''
# work out from system args whether we are running in pilot mode
PILOTING = core.setPilotModeFromArgs()
# start off with values from experiment settings
_fullScr = True
_winSize = [1440, 2560]
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']
    # replace default participant ID
    if prefs.piloting['replaceParticipantID']:
        expInfo['participant'] = 'pilot'

def showExpInfoDlg(expInfo):
    """
    Show participant info dialog.
    Parameters
    ==========
    expInfo : dict
        Information about this experiment.
    
    Returns
    ==========
    dict
        Information about this experiment.
    """
    # show participant info dialog
    dlg = gui.DlgFromDict(
        dictionary=expInfo, sortKeys=False, title=expName, alwaysOnTop=True
    )
    if dlg.OK == False:
        core.quit()  # user pressed cancel
    # return expInfo
    return expInfo


def setupData(expInfo, dataDir=None):
    """
    Make an ExperimentHandler to handle trials and saving.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    dataDir : Path, str or None
        Folder to save the data to, leave as None to create a folder in the current directory.    
    Returns
    ==========
    psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    # remove dialog-specific syntax from expInfo
    for key, val in expInfo.copy().items():
        newKey, _ = data.utils.parsePipeSyntax(key)
        expInfo[newKey] = expInfo.pop(key)
    
    # data file name stem = absolute path + name; later add .psyexp, .csv, .log, etc
    if dataDir is None:
        dataDir = _thisDir
    filename = u'data/%s_%s_%s' % (expInfo['participant'], expName, expInfo['date'])
    # make sure filename is relative to dataDir
    if os.path.isabs(filename):
        dataDir = os.path.commonprefix([dataDir, filename])
        filename = os.path.relpath(filename, dataDir)
    
    # an ExperimentHandler isn't essential but helps with data saving
    thisExp = data.ExperimentHandler(
        name=expName, version=expVersion,
        extraInfo=expInfo, runtimeInfo=None,
        originPath='D:\\Projects\\ABAmeta\\experiment\\staircasePsychopy_lastrun.py',
        savePickle=True, saveWideText=True,
        dataFileName=dataDir + os.sep + filename, sortColumns='time'
    )
    thisExp.setPriority('thisRow.t', priority.CRITICAL)
    thisExp.setPriority('expName', priority.LOW)
    # return experiment handler
    return thisExp


def setupLogging(filename):
    """
    Setup a log file and tell it what level to log at.
    
    Parameters
    ==========
    filename : str or pathlib.Path
        Filename to save log file and data files as, doesn't need an extension.
    
    Returns
    ==========
    psychopy.logging.LogFile
        Text stream to receive inputs from the logging system.
    """
    # set how much information should be printed to the console / app
    if PILOTING:
        logging.console.setLevel(
            prefs.piloting['pilotConsoleLoggingLevel']
        )
    else:
        logging.console.setLevel('warning')
    # save a log file for detail verbose info
    logFile = logging.LogFile(filename+'.log')
    if PILOTING:
        logFile.setLevel(
            prefs.piloting['pilotLoggingLevel']
        )
    else:
        logFile.setLevel(
            logging.getLevel('info')
        )
    
    return logFile


def setupWindow(expInfo=None, win=None):
    """
    Setup the Window
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    win : psychopy.visual.Window
        Window to setup - leave as None to create a new window.
    
    Returns
    ==========
    psychopy.visual.Window
        Window in which to run this experiment.
    """
    if PILOTING:
        logging.debug('Fullscreen settings ignored as running in pilot mode.')
    
    if win is None:
        # if not given a window to setup, make one
        win = visual.Window(
            size=_winSize, fullscr=_fullScr, screen=0,
            winType='pyglet', allowGUI=False, allowStencil=False,
            monitor='testMonitor', color=[0,0,0], colorSpace='rgb',
            backgroundImage='', backgroundFit='none',
            blendMode='avg', useFBO=True,
            units='height',
            checkTiming=False  # we're going to do this ourselves in a moment
        )
    else:
        # if we have a window, just set the attributes which are safe to set
        win.color = [0,0,0]
        win.colorSpace = 'rgb'
        win.backgroundImage = ''
        win.backgroundFit = 'none'
        win.units = 'height'
    if expInfo is not None:
        # get/measure frame rate if not already in expInfo
        if win._monitorFrameRate is None:
            win._monitorFrameRate = win.getActualFrameRate(infoMsg='Attempting to measure frame rate of screen, please wait...')
        expInfo['frameRate'] = win._monitorFrameRate
    win.hideMessage()
    if PILOTING:
        # show a visual indicator if we're in piloting mode
        if prefs.piloting['showPilotingIndicator']:
            win.showPilotingIndicator()
        # always show the mouse in piloting mode
        if prefs.piloting['forceMouseVisible']:
            win.mouseVisible = True
    
    return win


def setupDevices(expInfo, thisExp, win):
    """
    Setup whatever devices are available (mouse, keyboard, speaker, eyetracker, etc.) and add them to 
    the device manager (deviceManager)
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window in which to run this experiment.
    Returns
    ==========
    bool
        True if completed successfully.
    """
    # --- Setup input devices ---
    ioConfig = {}
    
    # Setup iohub keyboard
    ioConfig['Keyboard'] = dict(use_keymap='psychopy')
    
    # Setup iohub experiment
    ioConfig['Experiment'] = dict(filename=thisExp.dataFileName)
    
    # Start ioHub server
    ioServer = io.launchHubServer(window=win, **ioConfig)
    
    # store ioServer object in the device manager
    deviceManager.ioServer = ioServer
    
    # create a default keyboard (e.g. to check for escape)
    if deviceManager.getDevice('defaultKeyboard') is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='iohub'
        )
    if deviceManager.getDevice('startTrialspace') is None:
        # initialise startTrialspace
        startTrialspace = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='startTrialspace',
        )
    # create speaker 'trial_sound'
    deviceManager.addDevice(
        deviceName='trial_sound',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=4.0,
        resample='True',
        latencyClass=1,
    )
    if deviceManager.getDevice('space_release') is None:
        # initialise space_release
        space_release = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='space_release',
        )
    if deviceManager.getDevice('space_press') is None:
        # initialise space_press
        space_press = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='space_press',
        )
    # create speaker 'washout'
    deviceManager.addDevice(
        deviceName='washout',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=6.0,
        resample='True',
        latencyClass=1,
    )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], currentRoutine=None):
    """
    Pause this experiment, preventing the flow from advancing to the next routine until resumed.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    timers : list, tuple
        List of timers to reset once pausing is finished.
    currentRoutine : psychopy.data.Routine
        Current Routine we are in at time of pausing, if any. This object tells PsychoPy what Components to pause/play/dispatch.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # start a timer to figure out how long we're paused for
    pauseTimer = core.Clock()
    # pause any playback components
    if currentRoutine is not None:
        for comp in currentRoutine.getPlaybackComponents():
            comp.pause()
    # make sure we have a keyboard
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        defaultKeyboard = deviceManager.addKeyboard(
            deviceClass='keyboard',
            deviceName='defaultKeyboard',
            backend='ioHub',
        )
    # run a while loop while we wait to unpause
    while thisExp.status == PAUSED:
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=['escape']):
            endExperiment(thisExp, win=win)
        # dispatch messages on response components
        if currentRoutine is not None:
            for comp in currentRoutine.getDispatchComponents():
                comp.device.dispatchMessages()
        # sleep 1ms so other threads can execute
        clock.time.sleep(0.001)
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    if currentRoutine is not None:
        for comp in currentRoutine.getPlaybackComponents():
            comp.play()
    # reset any timers
    for timer in timers:
        timer.addTime(-pauseTimer.getTime())


def run(expInfo, thisExp, win, globalClock=None, thisSession=None):
    """
    Run the experiment flow.
    
    Parameters
    ==========
    expInfo : dict
        Information about this experiment, created by the `setupExpInfo` function.
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    psychopy.visual.Window
        Window in which to run this experiment.
    globalClock : psychopy.core.clock.Clock or None
        Clock to get global time from - supply None to make a new one.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    # mark experiment as started
    thisExp.status = STARTED
    # make sure window is set to foreground to prevent losing focus
    win.winHandle.activate()
    # make sure variables created by exec are available globally
    exec = environmenttools.setExecEnvironment(globals())
    # get device handles from dict of input devices
    ioServer = deviceManager.ioServer
    # get/create a default keyboard (e.g. to check for escape)
    defaultKeyboard = deviceManager.getDevice('defaultKeyboard')
    if defaultKeyboard is None:
        deviceManager.addDevice(
            deviceClass='keyboard', deviceName='defaultKeyboard', backend='ioHub'
        )
    eyetracker = deviceManager.getDevice('eyetracker')
    # make sure we're running in the directory for this experiment
    os.chdir(_thisDir)
    # get filename from ExperimentHandler for convenience
    filename = thisExp.dataFileName
    frameTolerance = 0.001  # how close to onset before 'same' frame
    endExpNow = False  # flag for 'escape' or other condition => quit the exp
    # get frame duration from frame rate in expInfo
    if 'frameRate' in expInfo and expInfo['frameRate'] is not None:
        frameDur = 1.0 / round(expInfo['frameRate'])
    else:
        frameDur = 1.0 / 60.0  # could not measure, so guess
    
    # Start Code - component code to be run after the window creation
    
    # --- Initialize components for Routine "setup" ---
    
    # --- Initialize components for Routine "startTrial" ---
    startTrialtxt = visual.TextStim(win=win, name='startTrialtxt',
        text='Press [space] to start the trial.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    startTrialspace = keyboard.Keyboard(deviceName='startTrialspace')
    
    # --- Initialize components for Routine "Trial" ---
    trial_cross = visual.ShapeStim(
        win=win, name='trial_cross', vertices='cross',
        size=(0.05, 0.05),
        ori=0.0, pos=(0, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor=[-1.0000, -1.0000, -1.0000],
        opacity=None, depth=0.0, interpolate=True)
    trial_sound = sound.Sound(
        'A', 
        secs=-1, 
        stereo=True, 
        hamming=True, 
        speaker='trial_sound',    name='trial_sound'
    )
    trial_sound.setVolume(0.2)
    space_release = keyboard.Keyboard(deviceName='space_release')
    space_press = keyboard.Keyboard(deviceName='space_press')
    
    # --- Initialize components for Routine "ITI" ---
    ITI_cross = visual.ShapeStim(
        win=win, name='ITI_cross', vertices='cross',
        size=(0.05, 0.05),
        ori=0.0, pos=(0, 0), draggable=False, anchor='center',
        lineWidth=1.0,
        colorSpace='rgb', lineColor='white', fillColor=[1.0000, 1.0000, 0.8824],
        opacity=None, depth=0.0, interpolate=True)
    washout = sound.Sound(
        'A', 
        secs=2, 
        stereo=True, 
        hamming=True, 
        speaker='washout',    name='washout'
    )
    washout.setVolume(0.1)
    
    # --- Initialize components for Routine "logJND" ---
    
    # create some handy timers
    
    # global clock to track the time since experiment started
    if globalClock is None:
        # create a clock if not given one
        globalClock = core.Clock()
    if isinstance(globalClock, str):
        # if given a string, make a clock accoridng to it
        if globalClock == 'float':
            # get timestamps as a simple value
            globalClock = core.Clock(format='float')
        elif globalClock == 'iso':
            # get timestamps in ISO format
            globalClock = core.Clock(format='%Y-%m-%d_%H:%M:%S.%f%z')
        else:
            # get timestamps in a custom format
            globalClock = core.Clock(format=globalClock)
    if ioServer is not None:
        ioServer.syncClock(globalClock)
    logging.setDefaultClock(globalClock)
    # routine timer to track time remaining of each (possibly non-slip) routine
    routineTimer = core.Clock()
    win.flip()  # flip window to reset last flip timer
    # store the exact time the global clock started
    expInfo['expStart'] = data.getDateStr(
        format='%Y-%m-%d %Hh%M.%S.%f %z', fractionalSecondDigits=6
    )
    
    # --- Prepare to start Routine "setup" ---
    # create an object to store info about Routine setup
    setup = data.Routine(
        name='setup',
        components=[],
    )
    setup.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # Run 'Begin Routine' code from code
    startingIntensity = 4.00
    stimDuration = 16
    hitThreshold = 0.5
    nRev = 6
    nTrials = 10
    stepSizes = [1.00,1.00,0.50,0.50,0.25,0.25]
    
    staircase = data.StairHandler(startVal = startingIntensity, nTrials = nTrials, nReversals= nRev, stepType='lin', minVal = 0.00, maxVal= 8.00, nUp = 1, nDown = 1, stepSizes = stepSizes)
    
    stimFile = 'stimuli\ABA\df_' + "{:.2f}".format(startingIntensity) + '_jitter_0.wav'
    
    def proportion_pressed(press_times, release_times, trial_duration=stimDuration):
        # Ensure lists are sorted
        press_times = sorted(press_times)
        release_times = sorted(release_times)
        
        intervals = []
        current_time = 0.0
        pressed = True  # Button starts pressed
    
        # Merge events into a timeline
        events = []
        for t in press_times:
            events.append((t, 'press'))
        for t in release_times:
            events.append((t, 'release'))
        events.sort()
    
        for t, event in events:
            if pressed:
                intervals.append((current_time, t))
            current_time = t
            pressed = (event == 'press')
    
        # If still pressed at the end, add the last interval
        if pressed and current_time < trial_duration:
            intervals.append((current_time, trial_duration))
    
        # Sum all pressed intervals
        pressed_time = sum(end - start for start, end in intervals)
        return pressed_time / trial_duration
    # store start times for setup
    setup.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    setup.tStart = globalClock.getTime(format='float')
    setup.status = STARTED
    thisExp.addData('setup.started', setup.tStart)
    setup.maxDuration = None
    # keep track of which components have finished
    setupComponents = setup.components
    for thisComponent in setup.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "setup" ---
    setup.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=setup,
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            setup.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in setup.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "setup" ---
    for thisComponent in setup.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for setup
    setup.tStop = globalClock.getTime(format='float')
    setup.tStopRefresh = tThisFlipGlobal
    thisExp.addData('setup.stopped', setup.tStop)
    thisExp.nextEntry()
    # the Routine "setup" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # set up handler to look after randomisation of conditions etc
    trialLoop = data.TrialHandler2(
        name='trialLoop',
        nReps=99.0, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
    )
    thisExp.addLoop(trialLoop)  # add the loop to the experiment
    thisTrialLoop = trialLoop.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisTrialLoop.rgb)
    if thisTrialLoop != None:
        for paramName in thisTrialLoop:
            globals()[paramName] = thisTrialLoop[paramName]
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    for thisTrialLoop in trialLoop:
        trialLoop.status = STARTED
        if hasattr(thisTrialLoop, 'status'):
            thisTrialLoop.status = STARTED
        currentLoop = trialLoop
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        # abbreviate parameter names if possible (e.g. rgb = thisTrialLoop.rgb)
        if thisTrialLoop != None:
            for paramName in thisTrialLoop:
                globals()[paramName] = thisTrialLoop[paramName]
        
        # --- Prepare to start Routine "startTrial" ---
        # create an object to store info about Routine startTrial
        startTrial = data.Routine(
            name='startTrial',
            components=[startTrialtxt, startTrialspace],
        )
        startTrial.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # create starting attributes for startTrialspace
        startTrialspace.keys = []
        startTrialspace.rt = []
        _startTrialspace_allKeys = []
        # store start times for startTrial
        startTrial.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        startTrial.tStart = globalClock.getTime(format='float')
        startTrial.status = STARTED
        thisExp.addData('startTrial.started', startTrial.tStart)
        startTrial.maxDuration = None
        # keep track of which components have finished
        startTrialComponents = startTrial.components
        for thisComponent in startTrial.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "startTrial" ---
        startTrial.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # if trial has changed, end Routine now
            if hasattr(thisTrialLoop, 'status') and thisTrialLoop.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *startTrialtxt* updates
            
            # if startTrialtxt is starting this frame...
            if startTrialtxt.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                startTrialtxt.frameNStart = frameN  # exact frame index
                startTrialtxt.tStart = t  # local t and not account for scr refresh
                startTrialtxt.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(startTrialtxt, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'startTrialtxt.started')
                # update status
                startTrialtxt.status = STARTED
                startTrialtxt.setAutoDraw(True)
            
            # if startTrialtxt is active this frame...
            if startTrialtxt.status == STARTED:
                # update params
                pass
            
            # *startTrialspace* updates
            waitOnFlip = False
            
            # if startTrialspace is starting this frame...
            if startTrialspace.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                startTrialspace.frameNStart = frameN  # exact frame index
                startTrialspace.tStart = t  # local t and not account for scr refresh
                startTrialspace.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(startTrialspace, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'startTrialspace.started')
                # update status
                startTrialspace.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(startTrialspace.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(startTrialspace.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if startTrialspace.status == STARTED and not waitOnFlip:
                theseKeys = startTrialspace.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                _startTrialspace_allKeys.extend(theseKeys)
                if len(_startTrialspace_allKeys):
                    startTrialspace.keys = _startTrialspace_allKeys[-1].name  # just the last key pressed
                    startTrialspace.rt = _startTrialspace_allKeys[-1].rt
                    startTrialspace.duration = _startTrialspace_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=startTrial,
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                startTrial.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in startTrial.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "startTrial" ---
        for thisComponent in startTrial.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for startTrial
        startTrial.tStop = globalClock.getTime(format='float')
        startTrial.tStopRefresh = tThisFlipGlobal
        thisExp.addData('startTrial.stopped', startTrial.tStop)
        # check responses
        if startTrialspace.keys in ['', [], None]:  # No response was made
            startTrialspace.keys = None
        trialLoop.addData('startTrialspace.keys',startTrialspace.keys)
        if startTrialspace.keys != None:  # we had a response
            trialLoop.addData('startTrialspace.rt', startTrialspace.rt)
            trialLoop.addData('startTrialspace.duration', startTrialspace.duration)
        # the Routine "startTrial" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        
        # --- Prepare to start Routine "Trial" ---
        # create an object to store info about Routine Trial
        Trial = data.Routine(
            name='Trial',
            components=[trial_cross, trial_sound, space_release, space_press],
        )
        Trial.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        trial_sound.setSound(stimFile, secs=stimDuration, hamming=True)
        trial_sound.setVolume(0.2, log=False)
        trial_sound.seek(0)
        # create starting attributes for space_release
        space_release.keys = []
        space_release.rt = []
        _space_release_allKeys = []
        # create starting attributes for space_press
        space_press.keys = []
        space_press.rt = []
        _space_press_allKeys = []
        # Run 'Begin Routine' code from spacebarCode
        countedKeysR = 0
        countedKeysP = 0
        # store start times for Trial
        Trial.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        Trial.tStart = globalClock.getTime(format='float')
        Trial.status = STARTED
        thisExp.addData('Trial.started', Trial.tStart)
        Trial.maxDuration = stimDuration
        # keep track of which components have finished
        TrialComponents = Trial.components
        for thisComponent in Trial.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "Trial" ---
        Trial.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # if trial has changed, end Routine now
            if hasattr(thisTrialLoop, 'status') and thisTrialLoop.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            # is it time to end the Routine? (based on local clock)
            if tThisFlip > Trial.maxDuration-frameTolerance:
                Trial.maxDurationReached = True
                continueRoutine = False
            
            # *trial_cross* updates
            
            # if trial_cross is starting this frame...
            if trial_cross.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                trial_cross.frameNStart = frameN  # exact frame index
                trial_cross.tStart = t  # local t and not account for scr refresh
                trial_cross.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(trial_cross, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'trial_cross.started')
                # update status
                trial_cross.status = STARTED
                trial_cross.setAutoDraw(True)
            
            # if trial_cross is active this frame...
            if trial_cross.status == STARTED:
                # update params
                pass
            
            # if trial_cross is stopping this frame...
            if trial_cross.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > trial_cross.tStartRefresh + stimDuration-frameTolerance:
                    # keep track of stop time/frame for later
                    trial_cross.tStop = t  # not accounting for scr refresh
                    trial_cross.tStopRefresh = tThisFlipGlobal  # on global time
                    trial_cross.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'trial_cross.stopped')
                    # update status
                    trial_cross.status = FINISHED
                    trial_cross.setAutoDraw(False)
            
            # *trial_sound* updates
            
            # if trial_sound is starting this frame...
            if trial_sound.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                trial_sound.frameNStart = frameN  # exact frame index
                trial_sound.tStart = t  # local t and not account for scr refresh
                trial_sound.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                thisExp.addData('trial_sound.started', tThisFlipGlobal)
                # update status
                trial_sound.status = STARTED
                trial_sound.play(when=win)  # sync with win flip
            
            # if trial_sound is stopping this frame...
            if trial_sound.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > trial_sound.tStartRefresh + stimDuration-frameTolerance or trial_sound.isFinished:
                    # keep track of stop time/frame for later
                    trial_sound.tStop = t  # not accounting for scr refresh
                    trial_sound.tStopRefresh = tThisFlipGlobal  # on global time
                    trial_sound.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'trial_sound.stopped')
                    # update status
                    trial_sound.status = FINISHED
                    trial_sound.stop()
            
            # *space_release* updates
            waitOnFlip = False
            
            # if space_release is starting this frame...
            if space_release.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                space_release.frameNStart = frameN  # exact frame index
                space_release.tStart = t  # local t and not account for scr refresh
                space_release.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(space_release, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'space_release.started')
                # update status
                space_release.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(space_release.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(space_release.clearEvents, eventType='keyboard')  # clear events on next screen flip
            
            # if space_release is stopping this frame...
            if space_release.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > space_release.tStartRefresh + stimDuration-frameTolerance:
                    # keep track of stop time/frame for later
                    space_release.tStop = t  # not accounting for scr refresh
                    space_release.tStopRefresh = tThisFlipGlobal  # on global time
                    space_release.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'space_release.stopped')
                    # update status
                    space_release.status = FINISHED
                    space_release.status = FINISHED
            if space_release.status == STARTED and not waitOnFlip:
                theseKeys = space_release.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=True)
                _space_release_allKeys.extend(theseKeys)
                if len(_space_release_allKeys):
                    space_release.keys = [key.name for key in _space_release_allKeys]  # storing all keys
                    space_release.rt = [key.rt for key in _space_release_allKeys]
                    space_release.duration = [key.duration for key in _space_release_allKeys]
            
            # *space_press* updates
            waitOnFlip = False
            
            # if space_press is starting this frame...
            if space_press.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                space_press.frameNStart = frameN  # exact frame index
                space_press.tStart = t  # local t and not account for scr refresh
                space_press.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(space_press, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'space_press.started')
                # update status
                space_press.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(space_press.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(space_press.clearEvents, eventType='keyboard')  # clear events on next screen flip
            
            # if space_press is stopping this frame...
            if space_press.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > space_press.tStartRefresh + stimDuration-frameTolerance:
                    # keep track of stop time/frame for later
                    space_press.tStop = t  # not accounting for scr refresh
                    space_press.tStopRefresh = tThisFlipGlobal  # on global time
                    space_press.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'space_press.stopped')
                    # update status
                    space_press.status = FINISHED
                    space_press.status = FINISHED
            if space_press.status == STARTED and not waitOnFlip:
                theseKeys = space_press.getKeys(keyList=['space'], ignoreKeys=["escape"], waitRelease=False)
                _space_press_allKeys.extend(theseKeys)
                if len(_space_press_allKeys):
                    space_press.keys = [key.name for key in _space_press_allKeys]  # storing all keys
                    space_press.rt = [key.rt for key in _space_press_allKeys]
                    space_press.duration = [key.duration for key in _space_press_allKeys]
            # Run 'Each Frame' code from spacebarCode
            if len(space_release.keys) > countedKeysR:
                countedKeysR += 1 # increase the keys that were counted
                #print('release') # sent the trigger
            
            if len(space_press.keys) > countedKeysP:
                countedKeysP += 1 # increase the keys that were counted
                #print('press') # sent the trigger
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=Trial,
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                Trial.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in Trial.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "Trial" ---
        for thisComponent in Trial.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for Trial
        Trial.tStop = globalClock.getTime(format='float')
        Trial.tStopRefresh = tThisFlipGlobal
        thisExp.addData('Trial.stopped', Trial.tStop)
        trial_sound.pause()  # ensure sound has stopped at end of Routine
        # check responses
        if space_release.keys in ['', [], None]:  # No response was made
            space_release.keys = None
        trialLoop.addData('space_release.keys',space_release.keys)
        if space_release.keys != None:  # we had a response
            trialLoop.addData('space_release.rt', space_release.rt)
            trialLoop.addData('space_release.duration', space_release.duration)
        # check responses
        if space_press.keys in ['', [], None]:  # No response was made
            space_press.keys = None
        trialLoop.addData('space_press.keys',space_press.keys)
        if space_press.keys != None:  # we had a response
            trialLoop.addData('space_press.rt', space_press.rt)
            trialLoop.addData('space_press.duration', space_press.duration)
        # the Routine "Trial" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
        
        # --- Prepare to start Routine "ITI" ---
        # create an object to store info about Routine ITI
        ITI = data.Routine(
            name='ITI',
            components=[ITI_cross, washout],
        )
        ITI.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        washout.setSound('stimuli/noise.wav', secs=2, hamming=True)
        washout.setVolume(0.1, log=False)
        washout.seek(0)
        # Run 'Begin Routine' code from prepNextTrial_2
        press_times = space_press.rt
        release_times = space_release.rt
        prop = proportion_pressed(press_times, release_times)
        
        if prop > hitThreshold:
            resp = 0
        else:
            resp = 1
        
        
        # store start times for ITI
        ITI.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        ITI.tStart = globalClock.getTime(format='float')
        ITI.status = STARTED
        thisExp.addData('ITI.started', ITI.tStart)
        ITI.maxDuration = None
        # keep track of which components have finished
        ITIComponents = ITI.components
        for thisComponent in ITI.components:
            thisComponent.tStart = None
            thisComponent.tStop = None
            thisComponent.tStartRefresh = None
            thisComponent.tStopRefresh = None
            if hasattr(thisComponent, 'status'):
                thisComponent.status = NOT_STARTED
        # reset timers
        t = 0
        _timeToFirstFrame = win.getFutureFlipTime(clock="now")
        frameN = -1
        
        # --- Run Routine "ITI" ---
        ITI.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine and routineTimer.getTime() < 2.0:
            # if trial has changed, end Routine now
            if hasattr(thisTrialLoop, 'status') and thisTrialLoop.status == STOPPING:
                continueRoutine = False
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *ITI_cross* updates
            
            # if ITI_cross is starting this frame...
            if ITI_cross.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                ITI_cross.frameNStart = frameN  # exact frame index
                ITI_cross.tStart = t  # local t and not account for scr refresh
                ITI_cross.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(ITI_cross, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'ITI_cross.started')
                # update status
                ITI_cross.status = STARTED
                ITI_cross.setAutoDraw(True)
            
            # if ITI_cross is active this frame...
            if ITI_cross.status == STARTED:
                # update params
                pass
            
            # if ITI_cross is stopping this frame...
            if ITI_cross.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > ITI_cross.tStartRefresh + 2-frameTolerance:
                    # keep track of stop time/frame for later
                    ITI_cross.tStop = t  # not accounting for scr refresh
                    ITI_cross.tStopRefresh = tThisFlipGlobal  # on global time
                    ITI_cross.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'ITI_cross.stopped')
                    # update status
                    ITI_cross.status = FINISHED
                    ITI_cross.setAutoDraw(False)
            
            # *washout* updates
            
            # if washout is starting this frame...
            if washout.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                washout.frameNStart = frameN  # exact frame index
                washout.tStart = t  # local t and not account for scr refresh
                washout.tStartRefresh = tThisFlipGlobal  # on global time
                # add timestamp to datafile
                thisExp.addData('washout.started', tThisFlipGlobal)
                # update status
                washout.status = STARTED
                washout.play(when=win)  # sync with win flip
            
            # if washout is stopping this frame...
            if washout.status == STARTED:
                # is it time to stop? (based on global clock, using actual start)
                if tThisFlipGlobal > washout.tStartRefresh + 2-frameTolerance or washout.isFinished:
                    # keep track of stop time/frame for later
                    washout.tStop = t  # not accounting for scr refresh
                    washout.tStopRefresh = tThisFlipGlobal  # on global time
                    washout.frameNStop = frameN  # exact frame index
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'washout.stopped')
                    # update status
                    washout.status = FINISHED
                    washout.stop()
            
            # check for quit (typically the Esc key)
            if defaultKeyboard.getKeys(keyList=["escape"]):
                thisExp.status = FINISHED
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer, globalClock], 
                    currentRoutine=ITI,
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                ITI.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in ITI.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "ITI" ---
        for thisComponent in ITI.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for ITI
        ITI.tStop = globalClock.getTime(format='float')
        ITI.tStopRefresh = tThisFlipGlobal
        thisExp.addData('ITI.stopped', ITI.tStop)
        washout.pause()  # ensure sound has stopped at end of Routine
        # Run 'End Routine' code from prepNextTrial_2
        staircase.addResponse(resp)  # response = 0 (integrated) or 1 (segregated)
        try:
            nextDF = staircase.next()
            feedback = f"Integrated percept time proportion: {prop}, Resp was therefore: {resp}, Next df will be: {nextDF:.2f}"
            print(feedback)
            stimFile = f"stimuli\ABA\df_{nextDF:.2f}_jitter_0.wav"
        except StopIteration:
            reversal_intensities = staircase.reversalIntensities
            jnd = sum(reversal_intensities) / len(reversal_intensities)
            trialLoop.finished = True
        # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
        if ITI.maxDurationReached:
            routineTimer.addTime(-ITI.maxDuration)
        elif ITI.forceEnded:
            routineTimer.reset()
        else:
            routineTimer.addTime(-2.000000)
        # mark thisTrialLoop as finished
        if hasattr(thisTrialLoop, 'status'):
            thisTrialLoop.status = FINISHED
        # if awaiting a pause, pause now
        if trialLoop.status == PAUSED:
            thisExp.status = PAUSED
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[globalClock], 
            )
            # once done pausing, restore running status
            trialLoop.status = STARTED
        thisExp.nextEntry()
        
    # completed 99.0 repeats of 'trialLoop'
    trialLoop.status = FINISHED
    
    if thisSession is not None:
        # if running in a Session with a Liaison client, send data up to now
        thisSession.sendExperimentData()
    
    # --- Prepare to start Routine "logJND" ---
    # create an object to store info about Routine logJND
    logJND = data.Routine(
        name='logJND',
        components=[],
    )
    logJND.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # Run 'Begin Routine' code from logJNDcode
    import pickle
    
    pID = expInfo['participant']
    outputDirectory = "pptJNDs/"
    os.makedirs(outputDirectory, exist_ok=True)
    
    
    jnd_path = outputDirectory + pID + "_jnd.pckl"
    
    with open(jnd_path, "wb") as f:
        pickle.dump(jnd, f)
    # store start times for logJND
    logJND.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    logJND.tStart = globalClock.getTime(format='float')
    logJND.status = STARTED
    thisExp.addData('logJND.started', logJND.tStart)
    logJND.maxDuration = None
    # keep track of which components have finished
    logJNDComponents = logJND.components
    for thisComponent in logJND.components:
        thisComponent.tStart = None
        thisComponent.tStop = None
        thisComponent.tStartRefresh = None
        thisComponent.tStopRefresh = None
        if hasattr(thisComponent, 'status'):
            thisComponent.status = NOT_STARTED
    # reset timers
    t = 0
    _timeToFirstFrame = win.getFutureFlipTime(clock="now")
    frameN = -1
    
    # --- Run Routine "logJND" ---
    logJND.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        
        # check for quit (typically the Esc key)
        if defaultKeyboard.getKeys(keyList=["escape"]):
            thisExp.status = FINISHED
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer, globalClock], 
                currentRoutine=logJND,
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            logJND.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in logJND.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "logJND" ---
    for thisComponent in logJND.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for logJND
    logJND.tStop = globalClock.getTime(format='float')
    logJND.tStopRefresh = tThisFlipGlobal
    thisExp.addData('logJND.stopped', logJND.tStop)
    thisExp.nextEntry()
    # the Routine "logJND" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # mark experiment as finished
    endExperiment(thisExp, win=win)


def saveData(thisExp):
    """
    Save data from this experiment
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    """
    filename = thisExp.dataFileName
    # these shouldn't be strictly necessary (should auto-save)
    thisExp.saveAsWideText(filename + '.csv', delim='auto')
    thisExp.saveAsPickle(filename)


def endExperiment(thisExp, win=None):
    """
    End this experiment, performing final shut down operations.
    
    This function does NOT close the window or end the Python process - use `quit` for this.
    
    Parameters
    ==========
    thisExp : psychopy.data.ExperimentHandler
        Handler object for this experiment, contains the data to save and information about 
        where to save it to.
    win : psychopy.visual.Window
        Window for this experiment.
    """
    if win is not None:
        # remove autodraw from all current components
        win.clearAutoDraw()
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed
        win.flip()
    # return console logger level to WARNING
    logging.console.setLevel(logging.WARNING)
    # mark experiment handler as finished
    thisExp.status = FINISHED
    # run any 'at exit' functions
    for fcn in runAtExit:
        fcn()
    logging.flush()


def quit(thisExp, win=None, thisSession=None):
    """
    Fully quit, closing the window and ending the Python process.
    
    Parameters
    ==========
    win : psychopy.visual.Window
        Window to close.
    thisSession : psychopy.session.Session or None
        Handle of the Session object this experiment is being run from, if any.
    """
    thisExp.abort()  # or data files will save again on exit
    # make sure everything is closed down
    if win is not None:
        # Flip one final time so any remaining win.callOnFlip() 
        # and win.timeOnFlip() tasks get executed before quitting
        win.flip()
        win.close()
    logging.flush()
    if thisSession is not None:
        thisSession.stop()
    # terminate Python process
    core.quit()


# if running this experiment as a script...
if __name__ == '__main__':
    # call all functions in order
    expInfo = showExpInfoDlg(expInfo=expInfo)
    thisExp = setupData(expInfo=expInfo)
    logFile = setupLogging(filename=thisExp.dataFileName)
    win = setupWindow(expInfo=expInfo)
    setupDevices(expInfo=expInfo, thisExp=thisExp, win=win)
    run(
        expInfo=expInfo, 
        thisExp=thisExp, 
        win=win,
        globalClock='float'
    )
    saveData(thisExp=thisExp)
    quit(thisExp=thisExp, win=win)
