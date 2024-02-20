clc; clear;
% Add path to utility functions
addpath('utils');
% Skip synchronization checks (we do not care)
Screen('Preference', 'SkipSyncTests', 1);
AssertOpenGL;
% Initialize with unified keynames and normalized colorspace:
PsychDefaultSetup(2);
% Force GetSecs and WaitSecs into memory to avoid latency later on:
GetSecs;  
WaitSecs(0.1);

% Get subject ID
subjectID = input('Enter subject ID: ', 's');

% Set parameters
p.results_dir = fullfile('./results', exp.subjID);
p.stimuli_dir = './stimuli';
p.stimuli_pattern = 'ABA_level_*.wav';
p.text_size = 30;
p.text_font = 'Arial';
p.back_color = [127 127 127];
p.fs = 44100;
% Setup key mapping:
p.key_response = KbName('SPACE');
p.key_quit = KbName('ESCAPE');
% Setup trigger parameters
p.runStartTrig = 100;
p.runEndTrig = 110;
p.pressTrig = 128; % binary:1000,0000. using only 8th bit to avoid overlap
p.trigLen = 10; % trigger pulse length = 10 ms

% Create results folder if doesn't exist
if ~isfolder(p.results_dir)
    mkdir(p.results_dir);
end 

% Set experimental infotmation
exp.name = 'ABA_pilot';
exp.date = nowstring;
exp.subjID = subjectID;
exp.conds = struct('n', {}, 'conds', struct('name', {}, 'path', {}, 'y', {}, 'fs', {}));
exp.runs = struct('n', 40, 'runs', struct());
exp.trial_duration = 7;
exp.validRespTime = 7;
exp.ITI = 3;
exp.minRunBreak = 5;

% Path to save experiment files
exp.filepath = fullfile(p.results_dir, sprintf('%s_%s_%s.mat', exp.name, exp.subjID, exp.date));

% Load conditions and corresponding audio files 
files = dir(fullfile(p.stimuli_dir,p.stimuli_pattern));
exp.conds.n = length(files);

for c = 1:exp.conds.n
    exp.conds(c).path = fullfile(files(c).folder, files(c).name);
    [exp.conds(c).y, exp.conds(c).fs] = audioread(exp.conds.files{c});
    exp.conds(c).name = files(c).name(1:end-4);
end

% Load audio device
InitializePsychSound;
p.pahandle = PsychPortAudio('Open', get_soundcard(), [], 0, p.fs, 2);
PsychPortAudio('Volume', p.pahandle, 0.5);

% Load silent audio to buffer
sound_load(fullfile('.', 'stimuli', 'silence.wav'), p.pahandle);
sound_play(p.pahandle);

% Detect StimTracker
device = stimtracker_detect();

try    
    % Open onscreen window with gray background:
    p.screenID = max(Screen('Screens'));
    PsychImaging('PrepareConfiguration');
    [p.whandle, p.wRect] = Screen('OpenWindow', p.screenID, p.back_color);
    
    % Define some usefull parameters based on screen size
    p.xCenter = floor(p.wRect(3)/2);
    p.yCenter = floor(p.wRect(4)/2);
    p.hpad = p.wRect(3)*0.05;
    p.vpad = p.wRect(4)*0.05;
    p.margin = p.wRect(4)*0.025;
    % p.progbar.frameRect = [p.wRect(3)/3, 2*p.wRect(4)/3, 2*p.wRect(3)/3, 2*p.wRect(4)/3+p.wRect(4)*0.04];
    % p.progbar.fillRect = p.progbar.frameRect + [3, 3, -3, -3];
    fixlinelength = 10;
    p.fixcross = [p.xCenter-fixlinelength p.xCenter+fixlinelength p.xCenter p.xCenter; ...
                  p.yCenter p.yCenter p.yCenter-fixlinelength p.yCenter+fixlinelength];
    p.fixwidth = 2.5;
    p.fixcolor = [1 1 1];

    % Initialize screen
    Screen('BlendFunction', p.whandle, GL_SRC_ALPHA, GL_ONE_MINUS_SRC_ALPHA);
    Screen('TextSize', p.whandle, p.text_size);
    HideCursor(p.whandle);
    
    %%%%%%%%%%%%%%%%%%%%%%% Wait Screen %%%%%%%%%%%%%%%%%%%%%%%
    str = 'Please wait for set up to finish.';
    aligned_text(p, str, 0, 2, 't', 'c')
    
    str = 'You will be taken to the experiment automatically.';
    aligned_text(p, str, 0, 3, 't', 'c')

    str = 'Thank you!';
    aligned_text(p, str, 0, 5, 't', 'c')

    str = 'CoNCH Lab';
    aligned_text(p, str, p.wRect(4), -3, 'c', 'c')

    Screen('Flip', p.whandle);

    KbWait([], 2);

    %%%%%%%%%%%%%%%%%%% Instructions Screen %%%%%%%%%%%%%%%%%%%
    str = '';
    aligned_text(p, str, 0, 1, 't', 'l')
    
    str = '';
    aligned_text(p, str, 0, 2, 't', 'l')

    str = "Hold the space button down if you're hearing two streams and release when you're hearing one.";
    aligned_text(p, str, 0, 3, 't', 'l')

    str = sprintf("You will complete %d runs, you can rest between runs.", exp.runs.n);
    aligned_text(p, str, 0, 12, 't', 'l')
    str = "Get ready and press any key to start.";
    aligned_text(p, str, 0, 13, 't', 'l')

    Screen('Flip', p.whandle);

    % Wait for button press
    KbWait([], 2);
    
    %%%%%%%%%%%%%%%%%%%%% ABA Pilot Task %%%%%%%%%%%%%%%%%%%%%%
    quitFlag = false;
    % Runs
    for r = 1:exp.runs.n
        % Draw fixation cross
        Screen('DrawLines',p.whandle,p.fixcross,p.fixwidth,p.fixcolor);
        Screen('DrawDots', p.whandle, [2550 10],100, [255 255 255],[0 0],4)
        Screen('Flip', p.whandle);
        
        % Send trigger at the begining of each run, duration is 10 ms
        send_Pulse(device, p.runStartTrig, p.trigLen);

        rng('shuffle');
        randind = randperm(exp.conds.n);

        run.run_number = r;
        run.n_trials = exp.conds.n;
        run.cond_order = randind;
        run.responses = NaN(1,run.n_trials);
        % run.trial_times = NaN(1,run.n_trials);
        run.RT = NaN(1,run.n_trials); % reaction time

        for n = 1:exp.numStim
            % Inter Trial Interval
            WaitSecs(exp.ITI);
            % Load and Play the sound
            sound_load(exp.conds.conds(run.cond_order(n)).path, p.pahandle);
            tic;
            stimtracker_sendtrigger(device, run.cond_order(n), p.trigLen);
            sound_play(p.pahandle);
           
            et = toc;
            while (et < exp.validRespTime)
                
                % % Show guide
                % str = 'What category this sound belongs to?';
                % drawAlignedText(p, str, 0, 5, 'c', 'c')
                % str = 'Animal (F) - Object (G) - People (H) - Scene (J)';
                % aligned_text(p, str, 0, 6, 't', 'c')
                % % Update progress bar
                % etr = et/exp.validRespTime; % Elapsed Time Ratio
                % x = (p.progbar.fillRect(3)-p.progbar.fillRect(1))*etr;
                % Screen('FrameRect', p.whandle ,[0 0 0] ,p.progbar.frameRect ,2);
                % Screen('FillRect', p.whandle ,[0 255 0] ,p.progbar.fillRect-[0 0 x 0] ,2);
                % % Flip screen
                % Screen('Flip', p.whandle);

                % Control buttons
                [keyIsDown, ~, keyCode] = KbCheck(-1);
                if (keyIsDown==1 && keyCode(p.key_response))
                    stimtracker_sendtrigger(device, p.pressTrig, 1);
                    run.responses(n) = 1;
                    if isnan(run.RT(n)), run.RT(n) = toc; end
                elseif (keyIsDown==1 && keyCode(p.key_quit))
                    quitFlag = true;
                end

                et = toc;
            end
            
            % % Save trial time
            % run.trialTimes(n)
            
            if quitFlag
                break;
            end
        end

        % Send trigger at the end of each run, duration is 10 ms
        send_Pulse(device, p.runEndTrig, p.trigLen);

        % Save run data in exp
        exp.runs.runs{end+1} = run;
        
        if quitFlag, break; end
        
        if r ~= exp.runs.n
            % Between runs break screen;
            str = sprintf('You completed %d runs out of %d.', r, exp.runs.n);
            aligned_text(p, str, p.wRect(4)/2, -2, 'c', 'c')
            str = 'Take a rest then press any key to continue.';
            aligned_text(p, str, p.wRect(4)/2, 0, 'c', 'c')
            Screen('Flip', p.whandle);
    
            WaitSecs(exp.minRunBreak)
            KbWait([], 2);
        end
    end

    % End screen
    str = "Great job! you are done.";
    aligned_text(p, str, p.wRect(4)/2, -2, 'c', 'c')
    str = "Press any key to exit.";
    aligned_text(p, str, p.wRect(4)/2, 0, 'c', 'c')
    Screen('Flip', p.whandle);

    KbWait([], 2);

    % Save exp and run information
    save(exp.filepath, 'exp', 'p');

    % Close audio port
    PsychPortAudio('Close', p.pahandle);
    % Show cursor again:
    ShowCursor(p.whandle);
    % Close screens.
    sca;
catch

    % Save exp and run information
    save(exp.filepath, 'exp', 'p');
    % Error handling: Close all p.whandle and audioport, release all ressources.
    PsychPortAudio('Close', p.pahandle);
    sca;
    rethrow(lasterror);  

end

