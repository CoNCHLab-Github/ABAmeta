% ABA Seqeucnes Meta Project - Pilot EEG Decoding: Stimuli
% Johnsrude lab: N. Zargarnezhad
% Stimulus Generation Main
close all
clear
clc

cd("D:\Projects\ABAmeta\stimGen")
addpath(genpath(pwd))

%% Constant variables and parameters
% Time and Frequency parameters
Fs = 48000; % Hz - sampling rate (The PsychoPy compatible sampling rate)
trial_len = 16; % s - trial duration
beep_len = 0.125; % s - beep sound duration (equal for A and B sequences)
init_silent_len = 0.125; % s - silent period length in the begining of the trial
trigger_len = 0.125; % s - trigger pulse duration
amp = -20; % db - envelope power

% Amplitude and envelope parameters
envelope_ramp_len = 0.05; % ratio - sin^2 envelope's ramp duration (between 0 to 0.5)

% Pitch parameters
FA = 400; % Hz - A seqeunce frequency
df_steps = 0.25; % semitones - delta f increment size
df_max = 8; % semitones - delta f max
df_min = 0; % semitones - delta f min

% Jitter parameters
jitter_steps = 1; % jitter increments in semitones
jitter_max = 4; % how many semitones above and below the base frequency
jitter_min = -4; % how many semitones below the base frequency

%% Amplitude Envelope
close all
clc

t_temp = 0:1/Fs:beep_len; % s - beep templates time variable
% sine^2 ramp amplitude envelope implementation
envelope = ones(1, length(t_temp));
envelope(t_temp<(envelope_ramp_len*beep_len)) = sin(2*pi*t_temp(t_temp<(envelope_ramp_len*beep_len))/(4*envelope_ramp_len*beep_len)).^2;
envelope(end-length(envelope(t_temp<(envelope_ramp_len*beep_len)))+1:end) = 1-envelope(t_temp<(envelope_ramp_len*beep_len));
envelope = db2mag(amp)*envelope; 
% visualization
%{
figure
plot(t_temp, envelope, "Color", 'k', 'LineWidth', 1.5)
xlim([t_temp(1), t_temp(end)])
ylim([-0.1, db2mag(amp)+0.2])
xlabel('T (s)')
ylabel('Envelope')
title(['Amplitude Envelope: ramp duration ratio = ', num2str(envelope_ramp_len)])
%}

%% A sequence
close all
clc

jitter = jitter_min:jitter_steps:jitter_max; % jitter values in semitones
FA = FA*(2.^(jitter/12)); % A sequence pitch values

% Generate A sequence
A = zeros(length(FA), 0);
t_A = zeros(length(FA), 0);
for i = 1:length(FA)
    [A_temp, t_temp] = make_sequence('A', FA(i), Fs, beep_len, envelope, trial_len);
    if i == 1
        A = zeros(length(FA), length(A_temp));
        t_A = zeros(length(FA), length(t_temp));
    end
    A(i,:) = A_temp;
    t_A(i,:) = t_temp;
end

%% B sequence
close all
clc

df = 0:df_steps:df_max; % delta f values in semitones
FB = zeros(length(FA), length(df)); % Preallocate FB for all FA and df combinations
for i = 1:length(FA)
    FB(i, :) = FA(i) * (2.^(df/12)); % B sequence pitch values for each FA
end

B = zeros(length(FB), length(t_A));
t_B = zeros(length(FB), length(t_A));

for i = 1:size(FB,1)
    for j = 1:size(FB,2)
        idx = (i-1)*size(FB,2) + j;
        [B(idx,:), t_B(idx,:)] = make_sequence('B', FB(i,j), Fs, beep_len, envelope, trial_len);
    end
end


%% Combine A and Bs
close all
clc

ABA = cell(length(FA), 1);
for i = 1:length(FA)
    ABA{i} = zeros(length(df), length(A));
    for j = 1:length(df)
        idx = (i-1)*length(df) + j;
        ABA{i}(j,:) = A(i,:) + B(idx,:);
    end
end


%% zero-padding, channel assignment, and saving the audio
close all
clc

t = 0:1/Fs:(init_silent_len+trial_len);
num_zeros = length(t) - length(t_A);

ABA_padded = cell(size(ABA));
for i = 1:length(ABA)
    ABA_padded{i} = [zeros(size(ABA{i},1), num_zeros), ABA{i}];
end


stimuli_dir = strcat(pwd, '/stimuliSorted');
if ~exist(stimuli_dir, 'dir')
       mkdir(stimuli_dir)
       addpath(stimuli_dir)
end

for i = 1:length(ABA_padded)
    for j = 1:size(ABA_padded{i}, 1)
        fname = sprintf('%s/df_%.2f_jitter_%d.wav', ...
            stimuli_dir,df(j), jitter(i));
        %fname = sprintf('%s/ABA_jitter_%d_df_%d_B_%.1fHz_A_%.1fHz.wav', ...
            %stimuli_dir, jitter(i), df(j), FB(i, j), FA(i));
        audiowrite(fname, ABA_padded{i}(j,:)', Fs);
    end
end


%% Functions
% local functions for stimuli generation

function beep = beep_temp(freq, Fs, beep_len, envelope)
    % This function builds the beep template for each sequence.
    
    t_temp = 0:1/Fs:beep_len;
    beep = sin(2*pi*freq*t_temp);
    beep = beep.*envelope;
end

function triplet_temp = seq_temp(temp, sequence_type)
    % This function builds the triplet hyper-template for each sequence.
    
    N = length(temp)-1;
    switch sequence_type
        case 'A'
            triplet_temp = temp; % the first A beep
            triplet_temp = [triplet_temp, zeros(1, N)]; % pause for a cycle (the first and last sample in the beep are zeros because of the envelope - overlapping with this zero padding)
            triplet_temp = [triplet_temp, temp(2:end)]; % the second A beep
            triplet_temp = [triplet_temp, zeros(1, N)]; % pause for a cycle
    
        case 'B'
            triplet_temp = zeros(1, N+1); % pause
            triplet_temp = [triplet_temp, temp(2:end)]; % B beep (the first and last samples overlap with the zeros in the pause periods)
            triplet_temp = [triplet_temp, zeros(1, 2*N)]; % pause for 2 cycles
    
    end
end

function [sequence, t] = make_sequence(type, freq, Fs, beep_len, envelope, trial_len)
    % This function makes a sequence of tone for the ABA_ sequence with the
    % given parameters.
    
    repetitions_num = ceil(trial_len/(4*beep_len));
    beep = beep_temp(freq, Fs, beep_len, envelope);
    triplet_temp = seq_temp(beep, type);
    sequence = triplet_temp;
    for i = 1:repetitions_num-1
        sequence = [sequence, triplet_temp(2:end)];
    end
    t_end = repetitions_num*4*beep_len;
    t = linspace(0, t_end, length(sequence));
    AWeighting = weightingFilter('A-weighting',Fs);
    sequence = AWeighting(sequence);
end
