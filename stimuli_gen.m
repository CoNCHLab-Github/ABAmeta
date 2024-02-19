% ABA Seqeucnes Meta Project - Pilot EEG Decoding: Stimuli
% Johnsrude lab: N. Zargarnezhad
% Stimulus Generation Main
close all
clear
clc

cd("/Users/nima/Desktop/Research/ABAmeta")
addpath(genpath(pwd))

%% Constant variables and parameters
% Time and Frequency parameters
Fs = 44100; % Hz - sampling rate (The Audio Dome's display sampling rate)
trial_len = 7; % s - trial duration
beep_len = 0.125; % s - beep sound duration (equal for A and B sequences)
init_silent_len = 0.125; % s - silent period length in the begining of the trial
trigger_len = 0.125; % s - trigger pulse duration
amp = -20; % db - envelope power

% Amplitude and envelope parameters
envelope_ramp_len = 0.05; % ratio - sin^2 envelope's ramp duration (between 0 to 0.5)

% Pitch parameters
FA = 400; % Hz - A seqeunce frequency
df_steps = 2; % semitones - delta f increment size
df_max = 8; % semitones - delta f max

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
figure
plot(t_temp, envelope, "Color", 'k', 'LineWidth', 1.5)
xlim([t_temp(1), t_temp(end)])
ylim([-0.1, db2mag(amp)+0.2])
xlabel('T (s)')
ylabel('Envelope')
title(['Amplitude Envelope: ramp duration ratio = ', num2str(envelope_ramp_len)])

%% A sequence
close all
clc

[A, t_A] = make_sequence('A', FA, Fs, beep_len, envelope, trial_len);

% visualization
figure
plot(t_A, A, "Color", "#0072BD")
xlim([t_A(1), t_A(end)])
ylim([-1.2, 1.2])
xlabel('T (s)')
ylabel('Amplitude')
title(['The A seqeunce with F_A = ', num2str(FA)])

%% B sequence
close all
clc

df = 0:df_steps:df_max; % delta f values in semitones
FB = FA*(2.^(df/12)); % B sequence pitch values

B = zeros(length(FB), length(t_A));
t_B = zeros(length(FB), length(t_A));

for i = 1:length(FB)
    [B(i,:), t_B(i,:)] = make_sequence('B', FB(i), Fs, beep_len, envelope, trial_len);
end

% visualization: a sample
sample = 1;
figure
plot(t_B(sample,:), B(sample,:), "Color", "#D95319")
xlim([t_B(sample, 1), t_B(sample, end)])
ylim([-1.2, 1.2])
xlabel('T (s)')
ylabel('Amplitude')
title(['The B seqeunce with F_B = ', num2str(FB(sample)), ' (\Deltaf = ', num2str(df(sample)), ' st)'])

%% Combine A and Bs
close all
clc

ABA = zeros(size(B));
for i = 1:size(B,1)
    ABA(i,:) = A + B(i,:);
end

% visualization: a sample
sample = 2;
figure
sgtitle(['ABA seqeunce with F_A = ', num2str(FA), ' Hz & F_B = ', num2str(FB(sample)), ' (\Deltaf = ', num2str(df(sample)), ' st)'])
subplot(2,1,1)
plot(t_A, ABA(sample,:), "Color", "Black")
xlim([t_A(1), t_A(end)])
ylim([-1.2, 1.2])

subplot(2,1,2)
plot(t_A, A, 'color', "#0072BD")
hold on
plot(t_B(sample,:), B(sample,:), "Color", "#D95319")
hold off
xlim([t_A(1), t_A(end)])
ylim([-1.2, 1.2])
xlabel('T (s)')
ylabel('Amplitude')

%% Trigger
trigger_pulse = zeros(1, length(t_A));
trigger_pulse(t_A<=trigger_len) = 1;

% visualization
figure
plot(t_A, trigger_pulse, "Color", "black")
xlim([t_A(1), t_A(end)])
ylim([-1.2, 1.2])
xlabel('T (s)')
ylabel('Amplitude')
title("Trigger Pulse")

%% zero-padding, channel assignment, and saving the audio
close all
clc

t = 0:1/Fs:(init_silent_len+trial_len);
num_zeros = length(t) - length(t_A);

ABA_padded = [zeros(size(ABA, 1), num_zeros), ABA];
trigger_pulse_padded = [zeros(1, num_zeros), trigger_pulse];

stimuli_dir = strcat(pwd, '/stimuli');
if ~exist(stimuli_dir, 'dir')
       mkdir(stimuli_dir)
       addpath(stimuli_dir)
end

for i = 1:size(ABA_padded,1)
    audiowrite(strcat(stimuli_dir,...
        '/ABA_level_', num2str(i),'_df_',...
        num2str(df(i)), 'st_B_', num2str(FB(i), '%.1f'),...
        'Hz_A_', num2str(FA), 'Hz.wav'),...
        [trigger_pulse_padded', ABA_padded(i,:)'], Fs);
end

% visualization: a sample
sample = 2;
figure
sgtitle(['ABA seqeunce with F_A = ', num2str(FA), ' Hz & F_B = ', num2str(FB(sample)), ' (\Deltaf = ', num2str(df(sample)), ' st)'])
subplot(3,1,1)
plot(t_A, A, 'color', "#0072BD")
hold on
plot(t_B(sample,:), B(sample,:), "Color", "#D95319")
hold off
xlim([t_A(1), t_A(end)])
ylim([-1.2, 1.2])
xlabel('T (s)')
ylabel('Amplitude')
title("ABA combined")
sound(ABA(sample,:), Fs)

subplot(3,1,2)
plot(t, ABA_padded(sample,:), "Color", "Black")
xlim([t(1), t(end)])
ylim([-1.2, 1.2])
title("ABA combined with initial silence period")

subplot(3,1,3)
plot(t, trigger_pulse_padded, "Color", "Black")
xlim([t(1), t(end)])
ylim([-1.2, 1.2])
title("The trigger pulse")

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
end
