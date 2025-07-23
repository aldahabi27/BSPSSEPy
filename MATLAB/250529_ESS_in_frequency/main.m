%% Set freq limit, compute sequence, and plot frequency
addpath(genpath("auxiliary_functions"))
addpath(genpath("Derivations and figures"))



clear
freq_limit = 1/60; % in p.u., set to large for inf Hz
T = 60; % total timesteps: 1Hz -> 70, 1.5Hz -> 50, inf Hz -> 40 

A250601_case9g_MILP; % solves the MILP for the action sequence

% save("newdata" + string(today("datetime")) + ".mat") % save data to file

A250601_plot_profile; % computes frequency profile and plots graph

A250601_output_formatting; % prepares output csv file
% csv file will be named plan + today's date


save("HarryPlotData" + string(today("datetime")) + ".mat");
