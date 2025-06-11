#!/usr/bin/env python
# -*- coding: utf-8 -*-
"""
This experiment was created using PsychoPy3 Experiment Builder (v2024.2.4),
    on June 04, 2025, at 16:29
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
prefs.hardware['audioLatencyMode'] = '3'
from psychopy import sound, gui, visual, core, data, event, logging, clock, colors, layout, hardware
from psychopy.tools import environmenttools
from psychopy.constants import (NOT_STARTED, STARTED, PLAYING, PAUSED,
                                STOPPED, FINISHED, PRESSED, RELEASED, FOREVER, priority)

import numpy as np  # whole numpy lib is available, prepend 'np.'
from numpy import (sin, cos, tan, log, log10, pi, average,
                   sqrt, std, deg2rad, rad2deg, linspace, asarray)
from numpy.random import random, randint, normal, shuffle, choice as randchoice
import os  # handy system and path functions
import sys  # to get file system encoding

import psychopy.iohub as io
from psychopy.hardware import keyboard

# This section of the EyeLink Initialize component code imports some
# modules we need, manages data filenames, allows for dummy mode configuration
# (for testing experiments without an eye tracker), connects to the tracker,
# and defines some helper functions (which can be called later)
import pylink
import time
import platform
from PIL import Image  # for preparing the Host backdrop image
from EyeLinkCoreGraphicsPsychoPy import EyeLinkCoreGraphicsPsychoPy
from string import ascii_letters, digits
from psychopy import gui

import psychopy_eyelink
print('EyeLink Plugin For PsychoPy Version = ' + str(psychopy_eyelink.__version__))

script_path = os.path.dirname(sys.argv[0])
if len(script_path) != 0:
    os.chdir(script_path)

# Set this variable to True if you use the built-in retina screen as your
# primary display device on macOS. If have an external monitor, set this
# variable True if you choose to "Optimize for Built-in Retina Display"
# in the Displays preference settings.
use_retina = False

# Set this variable to True to run the script in "Dummy Mode"
dummy_mode = False

# Prompt user to specify an EDF data filename
# before we open a fullscreen window
dlg_title = "Enter EDF Filename"
dlg_prompt = "Please enter a file name with 8 or fewer characters [letters, numbers, and underscore]."
# loop until we get a valid filename
while True:
    dlg = gui.Dlg(dlg_title)
    dlg.addText(dlg_prompt)
    dlg.addField("Filename",initial="Test",label="EDF Filename")
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:  # if ok_data is not None
        print("EDF data filename: {}".format(ok_data["Filename"]))
    else:
        print("user cancelled")
        core.quit()
        sys.exit()

    # get the string entered by the experimenter
    tmp_str = ok_data["Filename"]
    # strip trailing characters, ignore the ".edf" extension
    edf_fname = tmp_str.rstrip().split(".")[0]

    # check if the filename is valid (length <= 8 & no special char)
    allowed_char = ascii_letters + digits + "_"
    if not all([c in allowed_char for c in edf_fname]):
        print("ERROR: Invalid EDF filename")
    elif len(edf_fname) > 8:
        print("ERROR: EDF filename should not exceed 8 characters")
    else:
        break# Set up a folder to store the EDF data files and the associated resources
# e.g., files defining the interest areas used in each trial
results_folder = "results"
if not os.path.exists(results_folder):
    os.makedirs(results_folder)

# We download EDF data file from the EyeLink Host PC to the local hard
# drive at the end of each testing session, here we rename the EDF to
# include session start date/time
time_str = time.strftime("_%Y_%m_%d_%H_%M", time.localtime())
session_identifier = edf_fname + time_str

# create a folder for the current testing session in the "results" folder
session_folder = os.path.join(results_folder, session_identifier)
if not os.path.exists(session_folder):
    os.makedirs(session_folder)

# For macOS users check if they have a retina screen
if 'Darwin' in platform.system():
    dlg = gui.Dlg("Retina Screen?")
    dlg.addText("What type of screen will the experiment run on?")
    dlg.addField("Screen Type", choices=["High Resolution (Retina, 2k, 4k, 5k)", "Standard Resolution (HD or lower)"])
    # show dialog and wait for OK or Cancel
    ok_data = dlg.show()
    if dlg.OK:
        if dlg.data["Screen Type"] == "High Resolution (Retina, 2k, 4k, 5k)":  
            use_retina = True
        else:
            use_retina = False
    else:
        print('user cancelled')
        core.quit()
        sys.exit()

# Connect to the EyeLink Host PC
# The Host IP address, by default, is "100.1.1.1".
# the "el_tracker" objected created here can be accessed through the Pylink
# Set the Host PC address to "None" (without quotes) to run the script
# in "Dummy Mode"
if dummy_mode:
    el_tracker = pylink.EyeLink(None)
else:
    try:
        el_tracker = pylink.EyeLink("100.1.1.1")
    except RuntimeError as error:
        dlg = gui.Dlg("Dummy Mode?")
        dlg.addText("Could not connect to tracker at 100.1.1.1 -- continue in Dummy Mode?")
        # show dialog and wait for OK or Cancel
        ok_data = dlg.show()
        if dlg.OK:  # if ok_data is not None
            dummy_mode = True
            el_tracker = pylink.EyeLink(None)
        else:
            print("user cancelled")
            core.quit()
            sys.exit()

eyelinkThisFrameCallOnFlipScheduled = False
eyelinkLastFlipTime = 0.0
zeroTimeIAS = 0.0
zeroTimeDLF = 0.0
sentIASFileMessage = False
sentDrawListMessage = False

def clear_screen(win,genv):
    """ clear up the PsychoPy window"""
    win.fillColor = genv.getBackgroundColor()
    win.flip()

def show_msg(win, genv, text, wait_for_keypress=True):
    """ Show task instructions on screen"""
    scn_width, scn_height = win.size
    msg = visual.TextStim(win, text,
                          color=genv.getForegroundColor(),
                          wrapWidth=scn_width/2)
    clear_screen(win,genv)
    msg.draw()
    win.flip()

    # wait indefinitely, terminates upon any key press
    if wait_for_keypress:
        kb = keyboard.Keyboard()
        waitKeys = kb.waitKeys(keyList=None, waitRelease=True, clear=True)
        clear_screen(win,genv)

def terminate_task(win,genv,edf_file,session_folder,session_identifier):
    """ Terminate the task gracefully and retrieve the EDF data file
    """
    el_tracker = pylink.getEYELINK()

    if el_tracker.isConnected():
        # Terminate the current trial first if the task terminated prematurely
        error = el_tracker.isRecording()
        if error == pylink.TRIAL_OK:
            abort_trial(win,genv)

        # Put tracker in Offline mode
        el_tracker.setOfflineMode()

        # Clear the Host PC screen and wait for 500 ms
        el_tracker.sendCommand('clear_screen 0')
        pylink.msecDelay(500)

        # Close the edf data file on the Host
        el_tracker.closeDataFile()

        # Show a file transfer message on the screen
        msg = 'EDF data is transferring from EyeLink Host PC...'
        show_msg(win, genv, msg, wait_for_keypress=False)

        # Download the EDF data file from the Host PC to a local data folder
        # parameters: source_file_on_the_host, destination_file_on_local_drive
        local_edf = os.path.join(session_folder, session_identifier + '.EDF')
        try:
            el_tracker.receiveDataFile(edf_file, local_edf)
        except RuntimeError as error:
            print('ERROR:', error)

        # Close the link to the tracker.
        el_tracker.close()

    # close the PsychoPy window
    win.close()

    # quit PsychoPy
    core.quit()
    sys.exit()

def abort_trial(win,genv):
    """Ends recording """
    el_tracker = pylink.getEYELINK()

    # Stop recording
    if el_tracker.isRecording():
        # add 100 ms to catch final trial events
        pylink.pumpDelay(100)
        el_tracker.stopRecording()

    # clear the screen
    clear_screen(win,genv)
    # Send a message to clear the Data Viewer screen
    bgcolor_RGB = (116, 116, 116)
    el_tracker.sendMessage('!V CLEAR %d %d %d' % bgcolor_RGB)

    # send a message to mark trial end
    el_tracker.sendMessage('TRIAL_RESULT %d' % pylink.TRIAL_ERROR)
    return pylink.TRIAL_ERROR

# this method converts PsychoPy position values to EyeLink position values
# EyeLink position values are in pixel units and are such that 0,0 corresponds 
# to the top-left corner of the screen and increase as position moves right/down
def eyelink_pos(pos,winSize,unitType):
    screenUnitType = unitType
    scn_width,scn_height = winSize
    if screenUnitType == 'pix':
        elPos = [pos[0] + scn_width/2,scn_height/2 - pos[1]]
    elif screenUnitType == 'height':
        elPos = [scn_width/2 + pos[0] * scn_height,scn_height/2 + pos[1] * scn_height]
    elif screenUnitType == "norm":
        elPos = [(scn_width/2 * pos[0]) + scn_width/2,scn_height/2 + pos[1] * scn_height]
    else:
        print("ERROR:  Only pixel, height, and norm units supported for conversion to EyeLink position units")
    return [int(round(elPos[0])),int(round(elPos[1]))]

# this method converts PsychoPy size values to EyeLink size values
# EyeLink size values are in pixels
def eyelink_size(size,winSize,unitType):
    screenUnitType = unitType
    scn_width,scn_height = winSize
    if len(size) == 1:
        size = [size[0],size[0]]
    if screenUnitType == 'pix':
        elSize = [size[0],size[1]]
    elif screenUnitType == 'height':
        elSize = [int(round(scn_height*size[0])),int(round(scn_height*size[1]))]
    elif screenUnitType == "norm":
        elSize = [size[0]/2 * scn_width,size[1]/2 * scn_height]
    else:
        print("ERROR:  Only pixel, height, and norm units supported for conversion to EyeLink position units")
    return [int(round(elSize[0])),int(round(elSize[1]))]

# this method converts PsychoPy color values to EyeLink color values
def eyelink_color(color):
    elColor = (int(round((win.color[0]+1)/2*255)),int(round((win.color[1]+1)/2*255)),int(round((win.color[2]+1)/2*255)))
    return elColor


# This method, created by the EyeLink MarkEvents_space component code, will get called to handle
# sending event marking messages, logging Data Viewer (DV) stimulus drawing info, logging DV interest area info,
# sending DV Target Position Messages, and/or logging DV video frame marking info=information
def eyelink_onFlip_MarkEvents_space(globalClock,win,scn_width,scn_height,allStimComponentsForEyeLinkMonitoring,\
    componentsForEyeLinkStimEventMessages,\
    componentsForEyeLinkStimDVDrawingMessages,dlf,dlf_file):
    global eyelinkThisFrameCallOnFlipScheduled,eyelinkLastFlipTime,zeroTimeDLF,sentDrawListMessage
    # this variable becomes true whenever a component offsets, so we can 
    # send Data Viewer messgaes to clear the screen and redraw still-present 
    # components.  set it to false until a screen clear is needed
    needToUpdateDVDrawingFromScreenClear = False
    # store a list of all components that need Data Viewer drawing messages 
    # sent for this screen retrace
    componentsForDVDrawingList = []
    # Log the time of the current frame onset for upcoming messaging/event logging
    currentFrameTime = float(globalClock.getTime())

    # Go through all stimulus components that need to be checked (for event marking,
    # DV drawing, and/or interest area logging) to see if any have just ONSET
    for thisComponent in allStimComponentsForEyeLinkMonitoring:
        # Check if the component has just onset
        if thisComponent.tStartRefresh is not None and not thisComponent.elOnsetDetected:
            # Check whether we need to mark stimulus onset (and log a trial variable logging this time) for the component
            if thisComponent in componentsForEyeLinkStimEventMessages:
                el_tracker.sendMessage('%s %s_ONSET' % (int(round((globalClock.getTime()-thisComponent.tStartRefresh)*1000)),thisComponent.name))
                el_tracker.sendMessage('!V TRIAL_VAR %s_ONSET_TIME %i' % (thisComponent.name,thisComponent.tStartRefresh*1000))
                # Convert the component's position to EyeLink units and log this value under .elPos
                # Also create lastelPos/lastelSize to store pos/size of the previous position, which is needed for IAS file writing
                if thisComponent.componentType != 'sound':
                    thisComponent.elPos = eyelink_pos(thisComponent.pos,[scn_width,scn_height],thisComponent.units)
                    thisComponent.elSize = eyelink_size(thisComponent.size,[scn_width,scn_height],thisComponent.units)
                    thisComponent.lastelPos = thisComponent.elPos
                    thisComponent.lastelSize = thisComponent.elSize
            if not sentDrawListMessage and not dlf_file.closed:
                # send an IAREA FILE command message to let Data Viewer know where
                # to find the IAS file to load interest area information
                zeroTimeDLF = float(currentFrameTime)
                # send a DRAW_LIST command message to let Data Viewer know where
                # to find the drawing messages to correctly present the stimuli
                el_tracker.sendMessage('%s !V DRAW_LIST graphics/%s' % (int(round((globalClock.getTime()-currentFrameTime)*1000))-3,dlf))
                dlf_file.write('0 CLEAR %d %d %d\n' % eyelink_color(win.color))
                sentDrawListMessage = True

            if thisComponent in componentsForEyeLinkStimDVDrawingMessages:
                componentsForDVDrawingList.append(thisComponent)

            thisComponent.elOnsetDetected = True

    # Check whether any components that are being monitored for EyeLink purposes have changed position
    for thisComponent in allStimComponentsForEyeLinkMonitoring:
        if thisComponent.componentType != 'sound':
            # Get the updated position in EyeLink Units
            thisComponent.elPos = eyelink_pos(thisComponent.pos,[scn_width,scn_height],thisComponent.units)
            if thisComponent.elPos[0] != thisComponent.lastelPos[0] or thisComponent.elPos[1] != thisComponent.lastelPos[1]\
                and thisComponent.elOnsetDetected:
                # Only get an updated size if position has changed
                thisComponent.elSize = eyelink_size(thisComponent.size,[scn_width,scn_height],thisComponent.units)
                # log that we need to update the screen drawing with a clear command
                # and a redrawing of all still-present components
                if thisComponent in componentsForEyeLinkStimDVDrawingMessages:
                    needToUpdateDVDrawingFromScreenClear = True

                # update the position (in EyeLink coordinates) for upcoming usage
        if thisComponent.componentType != 'sound':
            thisComponent.lastelPos = thisComponent.elPos
            thisComponent.lastelSize = thisComponent.elSize
    # Go through all stimulus components that need to be checked (for event marking,
    # DV drawing, and/or interest area logging) to see if any have just OFFSET
    for thisComponent in allStimComponentsForEyeLinkMonitoring:
        # Check if the component has just offset
        if thisComponent.tStopRefresh is not None and thisComponent.tStartRefresh is not None and \
            not thisComponent.elOffsetDetected:
            # send a message marking that component's offset in the EDF
            if thisComponent in componentsForEyeLinkStimEventMessages:
                el_tracker.sendMessage('%s %s_OFFSET' % (int(round((globalClock.getTime()-thisComponent.tStopRefresh)*1000)),thisComponent.name))
            # log that we need to update the screen drawing with a clear command
            # and a redrawing of all still-present components
            if thisComponent in componentsForEyeLinkStimDVDrawingMessages:
                needToUpdateDVDrawingFromScreenClear = True
            thisComponent.elOffsetDetected = True 
    # Send drawing messages to the draw list file so that the stimuli/placeholders can be viewed in 
    # Data Viewer's Trial View window
    # See the Data Viewer User Manual, sections:
    # Protocol for EyeLink Data to Viewer Integration -> Image Commands/Simple Drawing Commands
    # If any component has offsetted on this frame then send a clear message
    # followed by logging to send draw commands for all still-present components
    if needToUpdateDVDrawingFromScreenClear and not dlf_file.closed:
        dlf_file.write('%i CLEAR ' % (int(round((zeroTimeDLF - currentFrameTime)*1000)))
            + '%d %d %d\n' % eyelink_color(win.color))

        for thisComponent in componentsForEyeLinkStimDVDrawingMessages:
            if thisComponent.elOnsetDetected and not thisComponent.elOffsetDetected and thisComponent not in componentsForDVDrawingList:
                componentsForDVDrawingList.append(thisComponent)

    for thisComponent in componentsForDVDrawingList:
        if not dlf_file.closed:
            # If it is an image component then send an image loading message
            if thisComponent.componentType == "Image":
                dlf_file.write('%i IMGLOAD CENTER ../../%s %i %i %i %i\n' % 
                    (int(round((zeroTimeDLF - currentFrameTime)*1000)),
                   thisComponent.image,thisComponent.elPos[0],
                    thisComponent.elPos[1],thisComponent.elSize[0],thisComponent.elSize[1]))
            # If it is a sound component then skip the stimulus drawing message
            elif thisComponent.componentType == "sound" or thisComponent.componentType == "MovieStim3" or thisComponent.componentType == "MovieStimWithFrameNum":
                pass
            # If it is any other non-movie visual stimulus component then send
            # a draw command to provide a placeholder box in Data Viewer's Trial View window
            else:
                dlf_file.write('%i DRAWBOX 255 0 0 %i %i %i %i\n' % 
                    (int(round((zeroTimeDLF - currentFrameTime)*1000)),
                    thisComponent.elPos[0]-thisComponent.elSize[0]/2,
                    thisComponent.elPos[1]-thisComponent.elSize[1]/2,
                    thisComponent.elPos[0]+thisComponent.elSize[0]/2,
                    thisComponent.elPos[1]+thisComponent.elSize[1]/2))
    # This logs whether a call to this method has already been scheduled for the upcoming retrace
    # And is used to help ensure we schedule only one callOnFlip call for each retrace
    eyelinkThisFrameCallOnFlipScheduled = False
    # This stores the time of the last retrace and can be used in Code components to 
    # check the time of the previous screen flip
    eyelinkLastFlipTime = float(currentFrameTime)
# --- Setup global variables (available in all functions) ---
# create a device manager to handle hardware (keyboards, mice, mirophones, speakers, etc.)
deviceManager = hardware.DeviceManager()
# ensure that relative paths start from the same directory as this script
_thisDir = os.path.dirname(os.path.abspath(__file__))
# store info about the experiment session
psychopyVersion = '2024.2.4'
expName = 'ABA_pilot'  # from the Builder filename that created this script
# information about this experiment
expInfo = {
    'participant': f"{randint(0, 999999):06.0f}",
    'session': '001',
    'runs': '10',
    'date|hid': data.getDateStr(),
    'expName|hid': expName,
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
_winSize = [1920, 1080]
# if in pilot mode, apply overrides according to preferences
if PILOTING:
    # force windowed mode
    if prefs.piloting['forceWindowed']:
        _fullScr = False
        # set window size
        _winSize = prefs.piloting['forcedWindowSize']

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
        name=expName, version='',
        extraInfo=expInfo, runtimeInfo=None,
        originPath='E:\\ABAMeta\\experiment\\ABA_pilot.py',
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
            logging.getLevel('warning')
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
    # show a visual indicator if we're in piloting mode
    if PILOTING and prefs.piloting['showPilotingIndicator']:
        win.showPilotingIndicator()
    
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
        index=4.0
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
    if deviceManager.getDevice('key_resp') is None:
        # initialise key_resp
        key_resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp',
        )
    if deviceManager.getDevice('key_resp_2') is None:
        # initialise key_resp_2
        key_resp_2 = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='key_resp_2',
        )
    # create speaker 'washout'
    deviceManager.addDevice(
        deviceName='washout',
        deviceClass='psychopy.hardware.speaker.SpeakerDevice',
        index=-1
    )
    if deviceManager.getDevice('break_key_resp') is None:
        # initialise break_key_resp
        break_key_resp = deviceManager.addDevice(
            deviceClass='keyboard',
            deviceName='break_key_resp',
        )
    # return True if completed successfully
    return True

def pauseExperiment(thisExp, win=None, timers=[], playbackComponents=[]):
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
    playbackComponents : list, tuple
        List of any components with a `pause` method which need to be paused.
    """
    # if we are not paused, do nothing
    if thisExp.status != PAUSED:
        return
    
    # start a timer to figure out how long we're paused for
    pauseTimer = core.Clock()
    # pause any playback components
    for comp in playbackComponents:
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
        # sleep 1ms so other threads can execute
        clock.time.sleep(0.001)
    # if stop was requested while paused, quit
    if thisExp.status == FINISHED:
        endExperiment(thisExp, win=win)
    # resume any playback components
    for comp in playbackComponents:
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
    
    # --- Initialize components for Routine "Prep" ---
    # Run 'Begin Experiment' code from stimSetup
    stimDuration = 16
    # This section of the EyeLink Initialize component code opens an EDF file,
    # writes some header text to the file, and configures some tracker settings
    el_tracker = pylink.getEYELINK()
    global edf_fname
    # Open an EDF data file on the Host PC
    edf_file = edf_fname + ".EDF"
    try:
        el_tracker.openDataFile(edf_file)
    except RuntimeError as err:
        print("ERROR:", err)
        # close the link if we have one open
        if el_tracker.isConnected():
            el_tracker.close()
        core.quit()
        sys.exit()
    
    # Add a header text to the EDF file to identify the current experiment name
    # This is OPTIONAL. If your text starts with "RECORDED BY " it will be
    # available in DataViewer's Inspector window by clicking
    # the EDF session node in the top panel and looking for the "Recorded By:"
    # field in the bottom panel of the Inspector.
    preamble_text = 'RECORDED BY %s EyeLink Plugin Version %s ' % (os.path.basename(__file__),psychopy_eyelink.__version__)
    el_tracker.sendCommand("add_file_preamble_text '%s'" % preamble_text)
    
    # Configure the tracker
    #
    # Put the tracker in offline mode before we change tracking parameters
    el_tracker.setOfflineMode()
    
    # Get the software version:  1-EyeLink I, 2-EyeLink II, 3/4-EyeLink 1000,
    # 5-EyeLink 1000 Plus, 6-Portable DUO
    eyelink_ver = 0  # set version to 0, in case running in Dummy mode
    if not dummy_mode:
        vstr = el_tracker.getTrackerVersionString()
        eyelink_ver = int(vstr.split()[-1].split(".")[0])
        # print out some version info in the shell
        print("Running experiment on %s, version %d" % (vstr, eyelink_ver))
    
    # File and Link data control
    # what eye events to save in the EDF file, include everything by default
    file_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,MESSAGE,BUTTON,INPUT'
    # what eye events to make available over the link, include everything by default
    link_event_flags = 'LEFT,RIGHT,FIXATION,SACCADE,BLINK,BUTTON,FIXUPDATE,INPUT'
    # what sample data to save in the EDF data file and to make available
    # over the link, include the 'HTARGET' flag to save head target sticker
    # data for supported eye trackers
    if eyelink_ver > 3:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,HTARGET,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,HTARGET,STATUS,INPUT'
    else:
        file_sample_flags = 'LEFT,RIGHT,GAZE,HREF,RAW,AREA,GAZERES,BUTTON,STATUS,INPUT'
        link_sample_flags = 'LEFT,RIGHT,GAZE,GAZERES,AREA,STATUS,INPUT'
    el_tracker.sendCommand("file_event_filter = %s" % file_event_flags)
    el_tracker.sendCommand("file_sample_data = %s" % file_sample_flags)
    el_tracker.sendCommand("link_event_filter = %s" % link_event_flags)
    el_tracker.sendCommand("link_sample_data = %s" % link_sample_flags)
    # Set a gamepad button to accept calibration/drift check target
    # You need a supported gamepad/button box that is connected to the Host PC
    el_tracker.sendCommand("button_function 5 'accept_target_fixation'")
    
    global eyelinkThisFrameCallOnFlipScheduled,eyelinkLastFlipTime,zeroTimeDLF,sentDrawListMessage,zeroTimeIAS,sentIASFileMessage
    
    # --- Initialize components for Routine "EyeSetup" ---
    Initialize = event.Mouse(win=win)
    CameraSetup = event.Mouse(win=win)
    
    # --- Initialize components for Routine "startTrial" ---
    startTrialtxt = visual.TextStim(win=win, name='startTrialtxt',
        text='Press [space] to start the trial.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    startTrialspace = keyboard.Keyboard(deviceName='startTrialspace')
    
    # --- Initialize components for Routine "EyeStart" ---
    StartRecord = event.Mouse(win=win)
    
    # --- Initialize components for Routine "Spacebar_Trial" ---
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
    trial_sound.setVolume(0.5)
    space_release = keyboard.Keyboard(deviceName='space_release')
    space_press = keyboard.Keyboard(deviceName='space_press')
    key_resp = keyboard.Keyboard(deviceName='key_resp')
    key_resp_2 = keyboard.Keyboard(deviceName='key_resp_2')
    MarkEvents_space = event.Mouse(win=win)
    
    # --- Initialize components for Routine "EyeStop" ---
    StopRecord = event.Mouse(win=win)
    
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
    washout.setVolume(0.5)
    
    # --- Initialize components for Routine "driftCheck" ---
    DriftCheck = event.Mouse(win=win)
    
    # --- Initialize components for Routine "Break" ---
    break_message = visual.TextStim(win=win, name='break_message',
        text='Take a break!\n\nPress space for the next block.',
        font='Arial',
        pos=(0, 0), draggable=False, height=0.05, wrapWidth=None, ori=0.0, 
        color='white', colorSpace='rgb', opacity=None, 
        languageStyle='LTR',
        depth=0.0);
    break_key_resp = keyboard.Keyboard(deviceName='break_key_resp')
    
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
    
    # --- Prepare to start Routine "Prep" ---
    # create an object to store info about Routine Prep
    Prep = data.Routine(
        name='Prep',
        components=[],
    )
    Prep.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # Run 'Begin Routine' code from stimSetup
    import pickle
    import random
    
    jitter = [-4,-3,-2,-1,0,1,2,3,4]
    
    pID = expInfo['participant']
    nBlocks = expInfo['runs']
    
    pptPickle = "pptJNDs/" + str(pID) + "_jnd.pckl"
    
    with open(pptPickle, "rb") as f:
        pptJND = pickle.load(f)
        
    pptJND = round(pptJND*4)/4
    # store start times for Prep
    Prep.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    Prep.tStart = globalClock.getTime(format='float')
    Prep.status = STARTED
    thisExp.addData('Prep.started', Prep.tStart)
    Prep.maxDuration = None
    # keep track of which components have finished
    PrepComponents = Prep.components
    for thisComponent in Prep.components:
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
    
    # --- Run Routine "Prep" ---
    Prep.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            Prep.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in Prep.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "Prep" ---
    for thisComponent in Prep.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for Prep
    Prep.tStop = globalClock.getTime(format='float')
    Prep.tStopRefresh = tThisFlipGlobal
    thisExp.addData('Prep.stopped', Prep.tStop)
    thisExp.nextEntry()
    # the Routine "Prep" was not non-slip safe, so reset the non-slip timer
    routineTimer.reset()
    
    # --- Prepare to start Routine "EyeSetup" ---
    # create an object to store info about Routine EyeSetup
    EyeSetup = data.Routine(
        name='EyeSetup',
        components=[Initialize, CameraSetup],
    )
    EyeSetup.status = NOT_STARTED
    continueRoutine = True
    # update component parameters for each repeat
    # store start times for EyeSetup
    EyeSetup.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
    EyeSetup.tStart = globalClock.getTime(format='float')
    EyeSetup.status = STARTED
    thisExp.addData('EyeSetup.started', EyeSetup.tStart)
    EyeSetup.maxDuration = None
    # keep track of which components have finished
    EyeSetupComponents = EyeSetup.components
    for thisComponent in EyeSetup.components:
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
    
    # --- Run Routine "EyeSetup" ---
    EyeSetup.forceEnded = routineForceEnded = not continueRoutine
    while continueRoutine and routineTimer.getTime() < 0.001:
        # get current time
        t = routineTimer.getTime()
        tThisFlip = win.getFutureFlipTime(clock=routineTimer)
        tThisFlipGlobal = win.getFutureFlipTime(clock=None)
        frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
        # update/draw components on each frame
        if thisExp.status == FINISHED or endExpNow:
            endExperiment(thisExp, win=win)
            return
        # pause experiment here if requested
        if thisExp.status == PAUSED:
            pauseExperiment(
                thisExp=thisExp, 
                win=win, 
                timers=[routineTimer], 
                playbackComponents=[]
            )
            # skip the frame we paused on
            continue
        
        # check if all components have finished
        if not continueRoutine:  # a component has requested a forced-end of Routine
            EyeSetup.forceEnded = routineForceEnded = True
            break
        continueRoutine = False  # will revert to True if at least one component still running
        for thisComponent in EyeSetup.components:
            if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                continueRoutine = True
                break  # at least one component has not yet finished
        
        # refresh the screen
        if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
            win.flip()
    
    # --- Ending Routine "EyeSetup" ---
    for thisComponent in EyeSetup.components:
        if hasattr(thisComponent, "setAutoDraw"):
            thisComponent.setAutoDraw(False)
    # store stop times for EyeSetup
    EyeSetup.tStop = globalClock.getTime(format='float')
    EyeSetup.tStopRefresh = tThisFlipGlobal
    thisExp.addData('EyeSetup.stopped', EyeSetup.tStop)
    # This section of the EyeLink Initialize component code gets graphic 
    # information from Psychopy, sets the screen_pixel_coords on the Host PC based
    # on these values, and logs the screen resolution for Data Viewer via 
    # a DISPLAY_COORDS message
    
    # get the native screen resolution used by PsychoPy
    scn_width, scn_height = win.size
    # resolution fix for Mac retina displays
    if 'Darwin' in platform.system():
        if use_retina:
            scn_width = int(scn_width/2.0)
            scn_height = int(scn_height/2.0)
    
    # Pass the display pixel coordinates (left, top, right, bottom) to the tracker
    # see the EyeLink Installation Guide, "Customizing Screen Settings"
    el_coords = "screen_pixel_coords = 0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendCommand(el_coords)
    
    # Write a DISPLAY_COORDS message to the EDF file
    # Data Viewer needs this piece of info for proper visualization, see Data
    # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
    dv_coords = "DISPLAY_COORDS  0 0 %d %d" % (scn_width - 1, scn_height - 1)
    el_tracker.sendMessage(dv_coords)# This Begin Experiment tab of the elTrial component just initializes
    # a trial counter variable at the beginning of the experiment
    trial_index = 1
    # Configure a graphics environment (genv) for tracker calibration
    genv = EyeLinkCoreGraphicsPsychoPy(el_tracker, win, True)
    print(genv)  # print out the version number of the CoreGraphics library
    
    # resolution fix for macOS retina display issues
    if use_retina:
        genv.fixMacRetinaDisplay()
    # Request Pylink to use the PsychoPy window we opened above for calibration
    pylink.openGraphicsEx(genv)
    # Create an array of pixels to assist in transferring content to the Host PC backdrop
    rgbBGColor = eyelink_color(win.color)
    blankHostPixels = [[rgbBGColor for i in range(scn_width)]
        for j in range(scn_height)]
    # This section of EyeLink CameraSetup component code configures some
    # graphics options for calibration, and then performs a camera setup
    # so that you can set up the eye tracker and calibrate/validate the participant
    # graphics options for calibration, and then performs a camera setup
    # so that you can set up the eye tracker and calibrate/validate the participant
    
    # Set background and foreground colors for the calibration target
    # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
    background_color = win.color
    foreground_color = (1,1,1)
    genv.setCalibrationColors(foreground_color, background_color)
    
    # Set up the calibration/validation target
    #
    # The target could be a "circle" (default), a "picture", a "movie" clip,
    # or a rotating "spiral". To configure the type of drift check target, set
    # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
    genv.setTargetType('circle')
    #
    genv.setTargetSize(24)
    
    # Beeps to play during calibration, validation and drift correction
    # parameters: target, good, error
    #     target -- sound to play when target moves
    #     good -- sound to play on successful operation
    #     error -- sound to play on failure or interruption
    # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
    genv.setCalibrationSounds('', '', '')
    
    # Choose a calibration type, H3, HV3, HV5, HV13 (HV = horizontal/vertical),
    el_tracker.sendCommand("calibration_type = " 'HV9')
    #clear the screen before we begin Camera Setup mode
    clear_screen(win,genv)
    
    
    # Go into Camera Setup mode so that participant setup/EyeLink calibration/validation can be performed
    # skip this step if running the script in Dummy Mode
    if not dummy_mode:
        try:
            el_tracker.doTrackerSetup()
        except RuntimeError as err:
            print('ERROR:', err)
            el_tracker.exitCalibration()
        else:
            win.mouseVisible = False
    # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
    if EyeSetup.maxDurationReached:
        routineTimer.addTime(-EyeSetup.maxDuration)
    elif EyeSetup.forceEnded:
        routineTimer.reset()
    else:
        routineTimer.addTime(-0.001000)
    thisExp.nextEntry()
    
    # set up handler to look after randomisation of conditions etc
    Blocks = data.TrialHandler2(
        name='Blocks',
        nReps=nBlocks, 
        method='random', 
        extraInfo=expInfo, 
        originPath=-1, 
        trialList=[None], 
        seed=None, 
    )
    thisExp.addLoop(Blocks)  # add the loop to the experiment
    thisBlock = Blocks.trialList[0]  # so we can initialise stimuli with some values
    # abbreviate parameter names if possible (e.g. rgb = thisBlock.rgb)
    if thisBlock != None:
        for paramName in thisBlock:
            globals()[paramName] = thisBlock[paramName]
    
    for thisBlock in Blocks:
        currentLoop = Blocks
        thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
        # abbreviate parameter names if possible (e.g. rgb = thisBlock.rgb)
        if thisBlock != None:
            for paramName in thisBlock:
                globals()[paramName] = thisBlock[paramName]
        
        # set up handler to look after randomisation of conditions etc
        trials = data.TrialHandler2(
            name='trials',
            nReps=1.0, 
            method='random', 
            extraInfo=expInfo, 
            originPath=-1, 
            trialList=data.importConditions('trials.xlsx'), 
            seed=None, 
        )
        thisExp.addLoop(trials)  # add the loop to the experiment
        thisTrial = trials.trialList[0]  # so we can initialise stimuli with some values
        # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
        if thisTrial != None:
            for paramName in thisTrial:
                globals()[paramName] = thisTrial[paramName]
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        for thisTrial in trials:
            currentLoop = trials
            thisExp.timestampOnFlip(win, 'thisRow.t', format=globalClock.format)
            if thisSession is not None:
                # if running in a Session with a Liaison client, send data up to now
                thisSession.sendExperimentData()
            # abbreviate parameter names if possible (e.g. rgb = thisTrial.rgb)
            if thisTrial != None:
                for paramName in thisTrial:
                    globals()[paramName] = thisTrial[paramName]
            
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
            # Run 'Begin Routine' code from pickStimFile
            pickedJitter = random.choice(jitter)
            
            if condition == 99:
                dfVal = pptJND
            else:
                dfVal = condition
            
            
            stimFile = "stimuli/ABA/" +  "df_" + "{:.2f}".format(dfVal) + "_jitter_" + str(pickedJitter) + ".wav"
            
            
            thisExp.addData('jitter', pickedJitter)
            thisExp.addData('stimFile', stimFile)
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
            # if trial has changed, end Routine now
            if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                continueRoutine = False
            startTrial.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
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
                    theseKeys = startTrialspace.getKeys(keyList=['space'], ignoreKeys=None, waitRelease=False)
                    _startTrialspace_allKeys.extend(theseKeys)
                    if len(_startTrialspace_allKeys):
                        startTrialspace.keys = _startTrialspace_allKeys[-1].name  # just the last key pressed
                        startTrialspace.rt = _startTrialspace_allKeys[-1].rt
                        startTrialspace.duration = _startTrialspace_allKeys[-1].duration
                        # a response ends the routine
                        continueRoutine = False
                # Run 'Each Frame' code from pickStimFile
                keys = event.getKeys()
                if 'b' in keys and 'p' in keys:
                        core.quit()
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
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
            trials.addData('startTrialspace.keys',startTrialspace.keys)
            if startTrialspace.keys != None:  # we had a response
                trials.addData('startTrialspace.rt', startTrialspace.rt)
                trials.addData('startTrialspace.duration', startTrialspace.duration)
            # the Routine "startTrial" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "EyeStart" ---
            # create an object to store info about Routine EyeStart
            EyeStart = data.Routine(
                name='EyeStart',
                components=[StartRecord],
            )
            EyeStart.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # store start times for EyeStart
            EyeStart.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            EyeStart.tStart = globalClock.getTime(format='float')
            EyeStart.status = STARTED
            thisExp.addData('EyeStart.started', EyeStart.tStart)
            EyeStart.maxDuration = None
            # keep track of which components have finished
            EyeStartComponents = EyeStart.components
            for thisComponent in EyeStart.components:
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
            
            # --- Run Routine "EyeStart" ---
            # if trial has changed, end Routine now
            if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                continueRoutine = False
            EyeStart.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 0.001:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    EyeStart.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in EyeStart.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "EyeStart" ---
            for thisComponent in EyeStart.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for EyeStart
            EyeStart.tStop = globalClock.getTime(format='float')
            EyeStart.tStopRefresh = tThisFlipGlobal
            thisExp.addData('EyeStart.stopped', EyeStart.tStop)
            # This section of EyeLink StartRecord component code starts eye tracker recording,
            # sends a trial start (i.e., TRIALID) message to the EDF, 
            # and logs which eye is tracked
            
            # get a reference to the currently active EyeLink connection
            el_tracker = pylink.getEYELINK()
            # Send a "TRIALID" message to mark the start of a trial, see the following Data Viewer User Manual:
            # "Protocol for EyeLink Data to Viewer Integration -> Defining the Start and End of a Trial"
            el_tracker.sendMessage('TRIALID %d' % trial_index)
            # Log the trial index at the start of recording in case there will be multiple trials within one recording
            trialIDAtRecordingStart = int(trial_index)
            # Log the routine index at the start of recording in case there will be multiple routines within one recording
            routine_index = 1
            # put tracker in idle/offline mode before recording
            el_tracker.setOfflineMode()
            # Start recording, logging all samples/events to the EDF and making all data available over the link
            # arguments: sample_to_file, events_to_file, sample_over_link, events_over_link (1-yes, 0-no)
            try:
                el_tracker.startRecording(1, 1, 1, 1)
            except RuntimeError as error:
                print("ERROR:", error)
                abort_trial(genv)
            # Allocate some time for the tracker to cache some samples before allowing
            # trial stimulus presentation to proceed
            pylink.pumpDelay(100)
            # determine which eye(s) is/are available
            # 0-left, 1-right, 2-binocular
            eye_used = el_tracker.eyeAvailable()
            if eye_used == 1:
                el_tracker.sendMessage("EYE_USED 1 RIGHT")
            elif eye_used == 0 or eye_used == 2:
                el_tracker.sendMessage("EYE_USED 0 LEFT")
                eye_used = 0
            else:
                print("ERROR: Could not get eye information!")
            #routineForceEnded = True
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if EyeStart.maxDurationReached:
                routineTimer.addTime(-EyeStart.maxDuration)
            elif EyeStart.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-0.001000)
            
            # --- Prepare to start Routine "Spacebar_Trial" ---
            # create an object to store info about Routine Spacebar_Trial
            Spacebar_Trial = data.Routine(
                name='Spacebar_Trial',
                components=[trial_cross, trial_sound, space_release, space_press, key_resp, key_resp_2, MarkEvents_space],
            )
            Spacebar_Trial.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            trial_sound.setSound(stimFile, secs=stimDuration, hamming=True)
            trial_sound.setVolume(0.5, log=False)
            trial_sound.seek(0)
            # create starting attributes for space_release
            space_release.keys = []
            space_release.rt = []
            _space_release_allKeys = []
            # create starting attributes for space_press
            space_press.keys = []
            space_press.rt = []
            _space_press_allKeys = []
            # Run 'Begin Routine' code from test
            countedKeysR = 0
            countedKeysP = 0
            # create starting attributes for key_resp
            key_resp.keys = []
            key_resp.rt = []
            _key_resp_allKeys = []
            # create starting attributes for key_resp_2
            key_resp_2.keys = []
            key_resp_2.rt = []
            _key_resp_2_allKeys = []
            # This section of EyeLink MarkEvents_space component code initializes some variables that will help with
            # sending event marking messages, logging Data Viewer (DV) stimulus drawing info, logging DV interest area info,
            # sending DV Target Position Messages, and/or logging DV video frame marking info
            # information
            
            
            # log trial variables' values to the EDF data file, for details, see Data
            # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
            trialConditionVariablesForEyeLinkLogging = [trig]
            trialConditionVariableNamesForEyeLinkLogging = ['trig']
            for i in range(len(trialConditionVariablesForEyeLinkLogging)):
                el_tracker.sendMessage('!V TRIAL_VAR %s %s'% (trialConditionVariableNamesForEyeLinkLogging[i],trialConditionVariablesForEyeLinkLogging[i]))
                #add a brief pause after every 5 messages or so to make sure no messages are missed
                if i % 5 == 0:
                    time.sleep(0.001)
            
            # list of all stimulus components whose onset/offset will be marked with messages
            componentsForEyeLinkStimEventMessages = [trial_sound]
            # list of all stimulus components for which Data Viewer draw commands will be sent
            componentsForEyeLinkStimDVDrawingMessages = [trial_sound]
            # create list of all components to be monitored for EyeLink Marking/Messaging
            allStimComponentsForEyeLinkMonitoring = componentsForEyeLinkStimEventMessages + componentsForEyeLinkStimDVDrawingMessages# make sure each component is only in the list once
            allStimComponentsForEyeLinkMonitoring = [*set(allStimComponentsForEyeLinkMonitoring)]
            # list of all response components whose onsets need to be marked and values
            # need to be logged
            componentsForEyeLinkRespEventMessages = [key_resp,key_resp_2]
            
            # Initialize stimulus components whose occurence needs to be monitored for event
            # marking, Data Viewer integration, and/or interest area messaging
            # to the EDF (provided they are supported stimulus types)
            for thisComponent in allStimComponentsForEyeLinkMonitoring:
                componentClassString = str(thisComponent.__class__)
                supportedStimType = False
                for stimType in ["Aperture","Text","Dot","Shape","Rect","Grating","Image","MovieStim3","Movie","sound"]:
                    if stimType in componentClassString:
                        supportedStimType = True
                        thisComponent.elOnsetDetected = False
                        thisComponent.elOffsetDetected = False
                        if stimType != "sound":
                            thisComponent.elPos = eyelink_pos(thisComponent.pos,[scn_width,scn_height],thisComponent.units)
                            thisComponent.elSize = eyelink_size(thisComponent.size,[scn_width,scn_height],thisComponent.units)
                            thisComponent.lastelPos = thisComponent.elPos
                            thisComponent.lastelSize = thisComponent.elSize
                        if stimType == "MovieStim3":
                            thisComponent.componentType = "MovieStim3"
                            thisComponent.elMarkingFrameIndex = -1
                            thisComponent.previousFrameTime = 0
                            thisComponent.firstFramePresented = False
                        elif stimType == "Movie":
                            thisComponent.componentType = "MovieStimWithFrameNum"
                            thisComponent.elMarkingFrameIndex = -1
                            thisComponent.firstFramePresented = False
                        else:
                            thisComponent.componentType = stimType
                        break   
                if not supportedStimType:
                    print("WARNING:  Stimulus component type " + str(thisComponent.__class__) + " not supported for EyeLink event marking")
                    print("          Event timing messages and/or Data Viewer drawing messages")
                    print("          will not be marked for this component")
                    print("          Consider marking the component via code component")
                    # remove unsupported types from our monitoring lists
                    allStimComponentsForEyeLinkMonitoring.remove(thisComponent)
                    componentsForEyeLinkStimEventMessages.remove(thisComponent)
                    componentsForEyeLinkStimDVDrawingMessages.remove(thisComponent)
                    componentsForEyeLinkInterestAreaMessages.remove(thisComponent)
            
            # Initialize response components whose occurence needs to be marked with 
            # a message to the EDF (provided they are supported stimulus types)
            # Supported types include mouse, keyboard, and any response component with an RT or time property
            for thisComponent in componentsForEyeLinkRespEventMessages:
                componentClassString = str(thisComponent.__class__)
                componentClassDir = dir(thisComponent)
                supportedRespType = False
                for respType in ["Mouse","Keyboard"]:
                    if respType in componentClassString:
                        thisComponent.componentType = respType
                        supportedRespType = True
                        break
                if not supportedRespType:
                    if "rt" in componentClassDir:
                        thisComponent.componentType = "OtherRespWithRT"
                        supportedRespType = True
                    elif "time" in componentClassDir:
                        thisComponent.componentType = "OtherRespWithTime"
                        supportedRespType = True
                if not supportedRespType:    
                        print("WARNING:  Response component type " + str(thisComponent.__class__) + " not supported for EyeLink event marking")
                        print("          Event timing will not be marked for this component")
                        print("          Please consider marking the component via code component")
                        # remove unsupported response types
                        componentsForEyeLinkRespEventMessages.remove(thisComponent)
            
            # Open a draw list file (DLF) to which Data Viewer drawing information will be logged
            # The commands that will be written to this DLF file will enable
            # Data Viewer to reproduce the stimuli in its Trial View window
            sentDrawListMessage = False
            # create a folder for the current testing session in the "results" folder
            drawList_folder = os.path.join(results_folder, session_identifier,"graphics")
            if not os.path.exists(drawList_folder):
                os.makedirs(drawList_folder)
            # open a DRAW LIST file to save the frame timing info for the video, which will
            # help us to be able to see the video in Data Viewer's Trial View window
            # See the Data Viewer User Manual section:
            # "Procotol for EyeLink Data to Viewer Integration -> Simple Drawing Commands"
            dlf = 'TRIAL_%04d_ROUTINE_%02d.dlf' % (trial_index,routine_index)
            dlf_file = open(os.path.join(drawList_folder, dlf), 'w')
            
            # Update a routine index for EyeLink IAS/DLF file logging -- 
            # Each routine will have its own set of IAS/DLF files, as each will have its own  Mark Events component
            routine_index = routine_index + 1
            # Send a Data Viewer clear screen command to clear its Trial View window
            # to the window color
            el_tracker.sendMessage('!V CLEAR %d %d %d' % eyelink_color(win.color))
            # create a keyboard instance and reinitialize a kePressNameList, which
            # will store list of key names currently being pressed (to allow Ctrl-C abort)
            kb = keyboard.Keyboard()
            keyPressNameList = []
            eyelinkThisFrameCallOnFlipScheduled = False
            eyelinkLastFlipTime = 0.0
            routineTimer.reset()
            # store start times for Spacebar_Trial
            Spacebar_Trial.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            Spacebar_Trial.tStart = globalClock.getTime(format='float')
            Spacebar_Trial.status = STARTED
            thisExp.addData('Spacebar_Trial.started', Spacebar_Trial.tStart)
            Spacebar_Trial.maxDuration = stimDuration
            # keep track of which components have finished
            Spacebar_TrialComponents = Spacebar_Trial.components
            for thisComponent in Spacebar_Trial.components:
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
            
            # --- Run Routine "Spacebar_Trial" ---
            # if trial has changed, end Routine now
            if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                continueRoutine = False
            Spacebar_Trial.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                # is it time to end the Routine? (based on local clock)
                if tThisFlip > Spacebar_Trial.maxDuration-frameTolerance:
                    Spacebar_Trial.maxDurationReached = True
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
                    theseKeys = space_release.getKeys(keyList=['space'], ignoreKeys=None, waitRelease=True)
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
                    theseKeys = space_press.getKeys(keyList=['space'], ignoreKeys=None, waitRelease=False)
                    _space_press_allKeys.extend(theseKeys)
                    if len(_space_press_allKeys):
                        space_press.keys = [key.name for key in _space_press_allKeys]  # storing all keys
                        space_press.rt = [key.rt for key in _space_press_allKeys]
                        space_press.duration = [key.duration for key in _space_press_allKeys]
                # Run 'Each Frame' code from test
                if len(space_release.keys) > countedKeysR:
                    countedKeysR += 1 # increase the keys that were counted
                    print('release') # sent the trigger
                
                if len(space_press.keys) > countedKeysP:
                    countedKeysP += 1 # increase the keys that were counted
                    print('press') # sent the trigger
                
                # *key_resp* updates
                waitOnFlip = False
                
                # if key_resp is starting this frame...
                if key_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp.frameNStart = frameN  # exact frame index
                    key_resp.tStart = t  # local t and not account for scr refresh
                    key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp.started')
                    # update status
                    key_resp.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp.getKeys(keyList=['y'], ignoreKeys=None, waitRelease=False)
                    _key_resp_allKeys.extend(theseKeys)
                    if len(_key_resp_allKeys):
                        key_resp.keys = [key.name for key in _key_resp_allKeys]  # storing all keys
                        key_resp.rt = [key.rt for key in _key_resp_allKeys]
                        key_resp.duration = [key.duration for key in _key_resp_allKeys]
                
                # *key_resp_2* updates
                waitOnFlip = False
                
                # if key_resp_2 is starting this frame...
                if key_resp_2.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                    # keep track of start time/frame for later
                    key_resp_2.frameNStart = frameN  # exact frame index
                    key_resp_2.tStart = t  # local t and not account for scr refresh
                    key_resp_2.tStartRefresh = tThisFlipGlobal  # on global time
                    win.timeOnFlip(key_resp_2, 'tStartRefresh')  # time at next scr refresh
                    # add timestamp to datafile
                    thisExp.timestampOnFlip(win, 'key_resp_2.started')
                    # update status
                    key_resp_2.status = STARTED
                    # keyboard checking is just starting
                    waitOnFlip = True
                    win.callOnFlip(key_resp_2.clock.reset)  # t=0 on next screen flip
                    win.callOnFlip(key_resp_2.clearEvents, eventType='keyboard')  # clear events on next screen flip
                if key_resp_2.status == STARTED and not waitOnFlip:
                    theseKeys = key_resp_2.getKeys(keyList=['n'], ignoreKeys=None, waitRelease=False)
                    _key_resp_2_allKeys.extend(theseKeys)
                    if len(_key_resp_2_allKeys):
                        key_resp_2.keys = [key.name for key in _key_resp_2_allKeys]  # storing all keys
                        key_resp_2.rt = [key.rt for key in _key_resp_2_allKeys]
                        key_resp_2.duration = [key.duration for key in _key_resp_2_allKeys]
                # This section of EyeLink MarkEvents_space component code checks whether to send (and sends/logs when appropriate)
                # event marking messages, log Data Viewer (DV) stimulus drawing info, log DV interest area info,
                # send DV Target Position Messages, and/or log DV video frame marking info
                if not eyelinkThisFrameCallOnFlipScheduled:
                    # This method, created by the EyeLink MarkEvents_space component code will get called to handle
                    # sending event marking messages, logging Data Viewer (DV) stimulus drawing info, logging DV interest area info,
                    # sending DV Target Position Messages, and/or logging DV video frame marking info=information
                    win.callOnFlip(eyelink_onFlip_MarkEvents_space,globalClock,win,scn_width,scn_height,allStimComponentsForEyeLinkMonitoring,\
                        componentsForEyeLinkStimEventMessages,\
                        componentsForEyeLinkStimDVDrawingMessages,dlf,dlf_file)
                    eyelinkThisFrameCallOnFlipScheduled = True
                
                # abort the current trial if the tracker is no longer recording
                error = el_tracker.isRecording()
                if error is not pylink.TRIAL_OK:
                    el_tracker.sendMessage('tracker_disconnected')
                    abort_trial(win,genv)
                
                # check keyboard events for experiment abort key combination
                keyPressList = kb.getKeys(keyList = ['lctrl','rctrl','c'], waitRelease = False, clear = False)
                for keyPress in keyPressList:
                    keyPressName = keyPress.name
                    if keyPressName not in keyPressNameList:
                        keyPressNameList.append(keyPress.name)
                if ('lctrl' in keyPressNameList or 'rctrl' in keyPressNameList) and 'c' in keyPressNameList:
                    el_tracker.sendMessage('terminated_by_user')
                    terminate_task(win,genv,edf_file,session_folder,session_identifier)
                #check for key releases
                keyReleaseList = kb.getKeys(keyList = ['lctrl','rctrl','c'], waitRelease = True, clear = False)
                for keyRelease in keyReleaseList:
                    keyReleaseName = keyRelease.name
                    if keyReleaseName in keyPressNameList:
                        keyPressNameList.remove(keyReleaseName)
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[trial_sound]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    Spacebar_Trial.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in Spacebar_Trial.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "Spacebar_Trial" ---
            for thisComponent in Spacebar_Trial.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for Spacebar_Trial
            Spacebar_Trial.tStop = globalClock.getTime(format='float')
            Spacebar_Trial.tStopRefresh = tThisFlipGlobal
            thisExp.addData('Spacebar_Trial.stopped', Spacebar_Trial.tStop)
            trial_sound.pause()  # ensure sound has stopped at end of Routine
            # check responses
            if space_release.keys in ['', [], None]:  # No response was made
                space_release.keys = None
            trials.addData('space_release.keys',space_release.keys)
            if space_release.keys != None:  # we had a response
                trials.addData('space_release.rt', space_release.rt)
                trials.addData('space_release.duration', space_release.duration)
            # check responses
            if space_press.keys in ['', [], None]:  # No response was made
                space_press.keys = None
            trials.addData('space_press.keys',space_press.keys)
            if space_press.keys != None:  # we had a response
                trials.addData('space_press.rt', space_press.rt)
                trials.addData('space_press.duration', space_press.duration)
            # check responses
            if key_resp.keys in ['', [], None]:  # No response was made
                key_resp.keys = None
            trials.addData('key_resp.keys',key_resp.keys)
            if key_resp.keys != None:  # we had a response
                trials.addData('key_resp.rt', key_resp.rt)
                trials.addData('key_resp.duration', key_resp.duration)
            # check responses
            if key_resp_2.keys in ['', [], None]:  # No response was made
                key_resp_2.keys = None
            trials.addData('key_resp_2.keys',key_resp_2.keys)
            if key_resp_2.keys != None:  # we had a response
                trials.addData('key_resp_2.rt', key_resp_2.rt)
                trials.addData('key_resp_2.duration', key_resp_2.duration)
            
            # This section of EyeLink MarkEvents_space component code does some event cleanup at the end of the routine
            # Go through all stimulus components that need to be checked for event marking,
            #  to see if the trial ended before PsychoPy reported OFFSET detection to mark their offset from trial end
            for thisComponent in componentsForEyeLinkStimEventMessages:
                if thisComponent.elOnsetDetected and not thisComponent.elOffsetDetected:
                    # Check if the component had onset but the trial ended before offset
                    el_tracker.sendMessage('%s_OFFSET' % (thisComponent.name))
            # Go through all response components whose occurence/data
            # need to be logged to the EDF and marks their occurence with a message (using an offset calculation that backstam
            for thisComponent in componentsForEyeLinkRespEventMessages:
                if thisComponent.componentType == "Keyboard" or thisComponent.componentType == "OtherRespWithRT":
                    if not isinstance(thisComponent.rt,list):
                        offsetValue = int(round((globalClock.getTime() - \
                            (thisComponent.tStartRefresh + thisComponent.rt))*1000))
                        el_tracker.sendMessage('%i %s_EVENT' % (offsetValue,thisComponent.componentType,))
                        # if sending many messages in a row, add a 1 msec pause between after
                        # every 5 messages or so
                    if isinstance(thisComponent.rt,list) and len(thisComponent.rt) > 0:
                        for i in range(len(thisComponent.rt)):
                            offsetValue = int(round((globalClock.getTime() - \
                                (thisComponent.tStartRefresh + thisComponent.rt[i]))*1000))
                            el_tracker.sendMessage('%i %s_EVENT_%i' % (offsetValue,thisComponent.componentType,i+1))
                            if i % 4 == 0:
                                # if sending many messages in a row, add a 1 msec pause between after 
                                # every 5 messages or so
                                time.sleep(0.001)
                    el_tracker.sendMessage('!V TRIAL_VAR %s.rt(s) %s' % (thisComponent.componentType,thisComponent.rt))
                    if "corr" in dir(thisComponent):
                        el_tracker.sendMessage('!V TRIAL_VAR %s.corr %s' % (thisComponent.componentType,thisComponent.corr))
                    if "keys" in dir(thisComponent):
                        el_tracker.sendMessage('!V TRIAL_VAR %s.keys %s' % (thisComponent.componentType,thisComponent.keys))
                elif thisComponent.componentType == "Mouse" or thisComponent.componentType == "OtherRespWithTime":
                    if not isinstance(thisComponent.time,list):
                        offsetValue = int(round((globalClock.getTime() - \
                            (thisComponent.tStartRefresh + thisComponent.time))*1000))
                        el_tracker.sendMessage('%i %s_EVENT' % (thisComponent.componentType,offsetValue))
                        # if sending many messages in a row, add a 1 msec pause between after 
                        # every 5 messages or so
                        time.sleep(0.0005)
                    if isinstance(thisComponent.time,list) and len(thisComponent.time) > 0:
                        for i in range(len(thisComponent.time)):
                            offsetValue = int(round((globalClock.getTime() - \
                                (thisComponent.tStartRefresh + thisComponent.time[i]))*1000))
                            el_tracker.sendMessage('%i %s_EVENT_%i' % (offsetValue,thisComponent.componentType,i+1))
                            if i % 4 == 0:
                                # if sending many messages in a row, add a 1 msec pause between after 
                                # every 5 messages or so
                                time.sleep(0.001)
                    el_tracker.sendMessage('!V TRIAL_VAR %s.time(s) %s' % (thisComponent.componentType,thisComponent.time))
                time.sleep(0.001)
            
            # close the drawlist file (which is used in Data Viewer stimulus presntation re-creation)
            dlf_file.close()
            
            # the Routine "Spacebar_Trial" was not non-slip safe, so reset the non-slip timer
            routineTimer.reset()
            
            # --- Prepare to start Routine "EyeStop" ---
            # create an object to store info about Routine EyeStop
            EyeStop = data.Routine(
                name='EyeStop',
                components=[StopRecord],
            )
            EyeStop.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # store start times for EyeStop
            EyeStop.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            EyeStop.tStart = globalClock.getTime(format='float')
            EyeStop.status = STARTED
            thisExp.addData('EyeStop.started', EyeStop.tStart)
            EyeStop.maxDuration = None
            # keep track of which components have finished
            EyeStopComponents = EyeStop.components
            for thisComponent in EyeStop.components:
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
            
            # --- Run Routine "EyeStop" ---
            # if trial has changed, end Routine now
            if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                continueRoutine = False
            EyeStop.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 0.001:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    EyeStop.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in EyeStop.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "EyeStop" ---
            for thisComponent in EyeStop.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for EyeStop
            EyeStop.tStop = globalClock.getTime(format='float')
            EyeStop.tStopRefresh = tThisFlipGlobal
            thisExp.addData('EyeStop.stopped', EyeStop.tStop)
            # This section of EyeLink StopRecord component code stops recording, sends a trial end (TRIAL_RESULT)
            # message to the EDF, and updates the trial_index variable 
            el_tracker.stopRecording()
            
            # send a 'TRIAL_RESULT' message to mark the end of trial, see Data
            # Viewer User Manual, "Protocol for EyeLink Data to Viewer Integration"
            el_tracker.sendMessage('TRIAL_RESULT %d' % 0)
            
            # update the trial counter for the next trial
            trial_index = trial_index + 1
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if EyeStop.maxDurationReached:
                routineTimer.addTime(-EyeStop.maxDuration)
            elif EyeStop.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-0.001000)
            
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
            washout.setVolume(0.5, log=False)
            washout.seek(0)
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
            # if trial has changed, end Routine now
            if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                continueRoutine = False
            ITI.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 2.0:
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
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[washout]
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
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if ITI.maxDurationReached:
                routineTimer.addTime(-ITI.maxDuration)
            elif ITI.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-2.000000)
            
            # --- Prepare to start Routine "driftCheck" ---
            # create an object to store info about Routine driftCheck
            driftCheck = data.Routine(
                name='driftCheck',
                components=[DriftCheck],
            )
            driftCheck.status = NOT_STARTED
            continueRoutine = True
            # update component parameters for each repeat
            # store start times for driftCheck
            driftCheck.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
            driftCheck.tStart = globalClock.getTime(format='float')
            driftCheck.status = STARTED
            thisExp.addData('driftCheck.started', driftCheck.tStart)
            driftCheck.maxDuration = None
            # keep track of which components have finished
            driftCheckComponents = driftCheck.components
            for thisComponent in driftCheck.components:
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
            
            # --- Run Routine "driftCheck" ---
            # if trial has changed, end Routine now
            if isinstance(trials, data.TrialHandler2) and thisTrial.thisN != trials.thisTrial.thisN:
                continueRoutine = False
            driftCheck.forceEnded = routineForceEnded = not continueRoutine
            while continueRoutine and routineTimer.getTime() < 0.001:
                # get current time
                t = routineTimer.getTime()
                tThisFlip = win.getFutureFlipTime(clock=routineTimer)
                tThisFlipGlobal = win.getFutureFlipTime(clock=None)
                frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
                # update/draw components on each frame
                if thisExp.status == FINISHED or endExpNow:
                    endExperiment(thisExp, win=win)
                    return
                # pause experiment here if requested
                if thisExp.status == PAUSED:
                    pauseExperiment(
                        thisExp=thisExp, 
                        win=win, 
                        timers=[routineTimer], 
                        playbackComponents=[]
                    )
                    # skip the frame we paused on
                    continue
                
                # check if all components have finished
                if not continueRoutine:  # a component has requested a forced-end of Routine
                    driftCheck.forceEnded = routineForceEnded = True
                    break
                continueRoutine = False  # will revert to True if at least one component still running
                for thisComponent in driftCheck.components:
                    if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                        continueRoutine = True
                        break  # at least one component has not yet finished
                
                # refresh the screen
                if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                    win.flip()
            
            # --- Ending Routine "driftCheck" ---
            for thisComponent in driftCheck.components:
                if hasattr(thisComponent, "setAutoDraw"):
                    thisComponent.setAutoDraw(False)
            # store stop times for driftCheck
            driftCheck.tStop = globalClock.getTime(format='float')
            driftCheck.tStopRefresh = tThisFlipGlobal
            thisExp.addData('driftCheck.stopped', driftCheck.tStop)
            # This section of EyeLink DriftCheck component code configures some
            # graphics options for drift check, and then performs the drift check
            # Set background and foreground colors for the drift check target
            # in PsychoPy, (-1, -1, -1)=black, (1, 1, 1)=white, (0, 0, 0)=mid-gray
            background_color = win.color
            foreground_color = (1,1,1)
            genv.setCalibrationColors(foreground_color, background_color)
            # Set up the drift check target
            # The target could be a "circle" (default), a "picture", a "movie" clip,
            # or a rotating "spiral". To configure the type of drift check target, set
            # genv.setTargetType to "circle", "picture", "movie", or "spiral", e.g.,
            genv.setTargetType('circle')
            genv.setTargetSize(24)
            # Beeps to play during calibration, validation and drift correction
            # parameters: target, good, error
            #     target -- sound to play when target moves
            #     good -- sound to play on successful operation
            #     error -- sound to play on failure or interruption
            # Each parameter could be ''--default sound, 'off'--no sound, or a wav file
            genv.setCalibrationSounds('off', 'off', 'off')
            
            # drift check
            # the doDriftCorrect() function requires target position in integers
            # the last two arguments:
            # draw_target (1-default, 0-draw the target then call doDriftCorrect)
            # allow_setup (1-press ESCAPE to recalibrate, 0-not allowed)
            
            # Skip drift-check if running the script in Dummy Mode
            while not dummy_mode:
                # terminate the task if no longer connected to the tracker or
                # user pressed Ctrl-C to terminate the task
                if (not el_tracker.isConnected()) or el_tracker.breakPressed():
                    terminate_task(win,genv,edf_file,session_folder,session_identifier)
                # drift-check and re-do camera setup if ESCAPE is pressed
                dcX,dcY = eyelink_pos([0,0],[scn_width,scn_height],'pix')
                try:
                    error = el_tracker.doDriftCorrect(int(round(dcX)),int(round(dcY)),1,1)
                    # break following a success drift-check
                    if error is not pylink.ESC_KEY:
                        break
                except:
                    pass
            # using non-slip timing so subtract the expected duration of this Routine (unless ended on request)
            if driftCheck.maxDurationReached:
                routineTimer.addTime(-driftCheck.maxDuration)
            elif driftCheck.forceEnded:
                routineTimer.reset()
            else:
                routineTimer.addTime(-0.001000)
            thisExp.nextEntry()
            
        # completed 1.0 repeats of 'trials'
        
        if thisSession is not None:
            # if running in a Session with a Liaison client, send data up to now
            thisSession.sendExperimentData()
        
        # --- Prepare to start Routine "Break" ---
        # create an object to store info about Routine Break
        Break = data.Routine(
            name='Break',
            components=[break_message, break_key_resp],
        )
        Break.status = NOT_STARTED
        continueRoutine = True
        # update component parameters for each repeat
        # create starting attributes for break_key_resp
        break_key_resp.keys = []
        break_key_resp.rt = []
        _break_key_resp_allKeys = []
        # store start times for Break
        Break.tStartRefresh = win.getFutureFlipTime(clock=globalClock)
        Break.tStart = globalClock.getTime(format='float')
        Break.status = STARTED
        thisExp.addData('Break.started', Break.tStart)
        Break.maxDuration = None
        # keep track of which components have finished
        BreakComponents = Break.components
        for thisComponent in Break.components:
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
        
        # --- Run Routine "Break" ---
        # if trial has changed, end Routine now
        if isinstance(Blocks, data.TrialHandler2) and thisBlock.thisN != Blocks.thisTrial.thisN:
            continueRoutine = False
        Break.forceEnded = routineForceEnded = not continueRoutine
        while continueRoutine:
            # get current time
            t = routineTimer.getTime()
            tThisFlip = win.getFutureFlipTime(clock=routineTimer)
            tThisFlipGlobal = win.getFutureFlipTime(clock=None)
            frameN = frameN + 1  # number of completed frames (so 0 is the first frame)
            # update/draw components on each frame
            
            # *break_message* updates
            
            # if break_message is starting this frame...
            if break_message.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                break_message.frameNStart = frameN  # exact frame index
                break_message.tStart = t  # local t and not account for scr refresh
                break_message.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(break_message, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'break_message.started')
                # update status
                break_message.status = STARTED
                break_message.setAutoDraw(True)
            
            # if break_message is active this frame...
            if break_message.status == STARTED:
                # update params
                pass
            
            # *break_key_resp* updates
            waitOnFlip = False
            
            # if break_key_resp is starting this frame...
            if break_key_resp.status == NOT_STARTED and tThisFlip >= 0.0-frameTolerance:
                # keep track of start time/frame for later
                break_key_resp.frameNStart = frameN  # exact frame index
                break_key_resp.tStart = t  # local t and not account for scr refresh
                break_key_resp.tStartRefresh = tThisFlipGlobal  # on global time
                win.timeOnFlip(break_key_resp, 'tStartRefresh')  # time at next scr refresh
                # add timestamp to datafile
                thisExp.timestampOnFlip(win, 'break_key_resp.started')
                # update status
                break_key_resp.status = STARTED
                # keyboard checking is just starting
                waitOnFlip = True
                win.callOnFlip(break_key_resp.clock.reset)  # t=0 on next screen flip
                win.callOnFlip(break_key_resp.clearEvents, eventType='keyboard')  # clear events on next screen flip
            if break_key_resp.status == STARTED and not waitOnFlip:
                theseKeys = break_key_resp.getKeys(keyList=['space'], ignoreKeys=None, waitRelease=False)
                _break_key_resp_allKeys.extend(theseKeys)
                if len(_break_key_resp_allKeys):
                    break_key_resp.keys = _break_key_resp_allKeys[-1].name  # just the last key pressed
                    break_key_resp.rt = _break_key_resp_allKeys[-1].rt
                    break_key_resp.duration = _break_key_resp_allKeys[-1].duration
                    # a response ends the routine
                    continueRoutine = False
            if thisExp.status == FINISHED or endExpNow:
                endExperiment(thisExp, win=win)
                return
            # pause experiment here if requested
            if thisExp.status == PAUSED:
                pauseExperiment(
                    thisExp=thisExp, 
                    win=win, 
                    timers=[routineTimer], 
                    playbackComponents=[]
                )
                # skip the frame we paused on
                continue
            
            # check if all components have finished
            if not continueRoutine:  # a component has requested a forced-end of Routine
                Break.forceEnded = routineForceEnded = True
                break
            continueRoutine = False  # will revert to True if at least one component still running
            for thisComponent in Break.components:
                if hasattr(thisComponent, "status") and thisComponent.status != FINISHED:
                    continueRoutine = True
                    break  # at least one component has not yet finished
            
            # refresh the screen
            if continueRoutine:  # don't flip if this routine is over or we'll get a blank screen
                win.flip()
        
        # --- Ending Routine "Break" ---
        for thisComponent in Break.components:
            if hasattr(thisComponent, "setAutoDraw"):
                thisComponent.setAutoDraw(False)
        # store stop times for Break
        Break.tStop = globalClock.getTime(format='float')
        Break.tStopRefresh = tThisFlipGlobal
        thisExp.addData('Break.stopped', Break.tStop)
        # check responses
        if break_key_resp.keys in ['', [], None]:  # No response was made
            break_key_resp.keys = None
        Blocks.addData('break_key_resp.keys',break_key_resp.keys)
        if break_key_resp.keys != None:  # we had a response
            Blocks.addData('break_key_resp.rt', break_key_resp.rt)
            Blocks.addData('break_key_resp.duration', break_key_resp.duration)
        # the Routine "Break" was not non-slip safe, so reset the non-slip timer
        routineTimer.reset()
    # completed nBlocks repeats of 'Blocks'
    
    # This section of the Initialize component calls the 
    # terminate_task helper function to get the EDF file and close the connection
    # to the Host PC
    
    # Disconnect, download the EDF file, then terminate the task
    terminate_task(win,genv,edf_file,session_folder,session_identifier)
    
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
