function aligned_text(p, str, voffset_px, voffset_lines, valign, halign)
% This is a Psychtoolbox wrapper function to draw aligned text on the screen.
% Inputs: 
%   p: parameters struct
%   str: string to draw
%   voffset_px: vertical offset of the text anchor (pixels)
%   voffset_lines: vertical offset of the text anchor (lines)
%   valign: vertical alignment of the text with respect to the text anchor
%       valid values: 't' / 'top' (default), 'b' / 'bottom', and 'c' / 'center'
%   halign: horizontal alignment of the text with respect to the screen
%       valid values: 'l' / 'left' (default), 'r' / 'right', and 'c' / 'center'
%
% Author: Ali Tafakkor (atafakko@uwo.ca, alitafakkor@gmail.com) 2024

% Set default values for halign ('left') and valign ('top')
if nargin < 5, halign = 'left'; valign = 'top'; end
% Get text size in pixels
text_size = Screen('TextBounds', p.whandle, str);
% Calculate horizontal location (x) of the text according to halign
switch halign
    case {'left', 'l'}
        x = p.hpad;
    case {'center', 'c'}
        x = p.xCenter - text_size(3)/2;
    case {'right', 'r'}
        x = p.wRect(3) - text_size(3) - p.hpad;
    otherwise
        error('Invalid horizontal align argument!')
end
% Calculate vertical location (y) of the text according to valign
switch valign
    case {'top', 't'}
        y = p.hpad + (text_size(4)+p.margin)*voffset_lines;
    case {'center', 'c'}
        y = p.hpad + (text_size(4)+p.margin)*voffset_lines - text_size(4)/2;
    case {'bottom', 'b'}
        y = p.hpad + (text_size(4)+p.margin)*voffset_lines + text_size(4)/2;
    otherwise
        error('Invalid vertical align argument!')
end
% Add vertical offset (pixels)
y = y + voffset_px;
% Draw text at desired position
Screen('DrawText', p.whandle, str, x, y, [0 0 0]);