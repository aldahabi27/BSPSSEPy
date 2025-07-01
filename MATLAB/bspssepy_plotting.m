% This code is to plot the simulation output from the selected csv file
% (exported by bspssepy).
%
%
% Last updated 30 June 2025

clear;
clc;
close all;

csv_file = "I:\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\Simulations\IEEE9_Ver17_092539_280625.csv";
csv_file = "I:\Work\Research\Control & Power Systems\JWSP Research\HONI Project\PSSE\BSPSSEPy\case\IEEE9\Simulations\IEEE9_Ver17_172347_300625.csv";

opts = delimitedTextImportOptions('DataLines',3,VariableNamesLine=2,VariableNamingRule='preserve');
bspssepy_data = readtable(csv_file ,opts,"ReadVariableNames", true);


freq_index = find(startsWith(bspssepy_data.Properties.VariableNames, 'freq', 'IgnoreCase',true));

freq = cellfun(@str2double, table2array(bspssepy_data(:,freq_index)));

[~, i_freq_avg] = max(abs(freq) > 0.00000001,[],1);

freq_mask = bsxfun(@gt, (1:size(freq,1))', i_freq_avg);
freq_nan = freq;
freq_nan(~freq_mask) = NaN;
avg_freq = mean(freq_nan,2, 'omitnan');
avg_freq(isnan(avg_freq)) = 0;

% convert freq to hz
avg_freq = avg_freq.*60;

time_index = find(startsWith(bspssepy_data.Properties.VariableNames, 'time', 'IgnoreCase',true));
time = cellfun(@str2double, table2array(bspssepy_data(:,time_index)));

% convert time to mins
time = time./60;

% convert time to "timestep number"
time = time./2;

%% plot the avg_freq

h = figure(1);
plot(time-1, avg_freq,'-m',  'LineWidth',2)

grid on

xlabel('time (mins)')
ylabel('f (Hz)')
%% Plot individual frequencies for each generator!
h = figure(2);
hold on
my_legend = {};

plot(time-1, freq_nan(:,1), 'LineWidth',3);
my_legend = [my_legend, {"Gen1"}];

plot(time-1, freq_nan(:,2), 'LineWidth',2);
my_legend = [my_legend, {"Gen2"}];

plot(time-1, freq_nan(:,3));
my_legend = [my_legend, {"Gen3"}];

plot(time-1, freq_nan(:,4));
my_legend = [my_legend, {"BESS"}];


myleg = legend(my_legend, "location", "north");

xlabel('time (mins)')
ylabel('f (Hz)')

grid on
myleg.NumColumns = 3;




%% Plot all info about all generators with subplots!
h = figure(4)

Gen1_index = find(endsWith(bspssepy_data.Properties.VariableNames, 'gen1', 'IgnoreCase',true));
Gen2_index = find(endsWith(bspssepy_data.Properties.VariableNames, 'gen2', 'IgnoreCase',true));
Gen3_index = find(endsWith(bspssepy_data.Properties.VariableNames, 'gen3', 'IgnoreCase',true));
BESS5_index = find(endsWith(bspssepy_data.Properties.VariableNames, 'bess5', 'IgnoreCase',true));

subplot(2,4,1); % GREF
hold on
GREF1 = cellfun(@str2double, table2array(bspssepy_data(:,Gen1_index(1))));
GREF2 = cellfun(@str2double, table2array(bspssepy_data(:,Gen2_index(1))));
GREF3 = cellfun(@str2double, table2array(bspssepy_data(:,Gen3_index(1))));
BESS5_PREF = cellfun(@str2double, table2array(bspssepy_data(:,BESS5_index(1))));

my_legend = {};
plot(time-1, GREF1, 'LineWidth', 3);
my_legend = [my_legend, {"Gen1"}];
plot(time-1, GREF2, 'LineWidth', 3);
my_legend = [my_legend, {"Gen2"}];
plot(time-1, GREF3, 'LineWidth', 3);
my_legend = [my_legend, {"Gen3"}];
plot(time-1, BESS5_PREF, 'LineWidth', 3);
my_legend = [my_legend, {"BESS5"}];


myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$G_{\mathsf{ref}}$", "Interpreter", "latex");


subplot(2,4,2); % VREF
hold on
VREF1 = cellfun(@str2double, table2array(bspssepy_data(:,Gen1_index(2))));
VREF2 = cellfun(@str2double, table2array(bspssepy_data(:,Gen2_index(2))));
VREF3 = cellfun(@str2double, table2array(bspssepy_data(:,Gen3_index(2))));
BESS5_QREF = cellfun(@str2double, table2array(bspssepy_data(:,BESS5_index(2))));

my_legend = {};
plot(time-1, VREF1, 'LineWidth', 3);
my_legend = [my_legend, {"Gen1"}];
plot(time-1, VREF2, 'LineWidth', 3);
my_legend = [my_legend, {"Gen2"}];
plot(time-1, VREF3, 'LineWidth', 3);
my_legend = [my_legend, {"Gen3"}];
plot(time-1, BESS5_QREF, 'LineWidth', 3);
my_legend = [my_legend, {"BESS5"}];


myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$V_{\mathsf{ref}}$", "Interpreter", "latex");


subplot(2,4,3); % PELEC
hold on
PELEC1 = cellfun(@str2double, table2array(bspssepy_data(:,Gen1_index(3))));
PELEC2 = cellfun(@str2double, table2array(bspssepy_data(:,Gen2_index(3))));
PELEC3 = cellfun(@str2double, table2array(bspssepy_data(:,Gen3_index(3))));
BESS5_PELEC = cellfun(@str2double, table2array(bspssepy_data(:,BESS5_index(3))));

my_legend = {};
plot(time-1, PELEC1, 'LineWidth', 3);
my_legend = [my_legend, {"Gen1"}];
plot(time-1, PELEC2, 'LineWidth', 3);
my_legend = [my_legend, {"Gen2"}];
plot(time-1, PELEC3, 'LineWidth', 3);
my_legend = [my_legend, {"Gen3"}];
plot(time-1, BESS5_PELEC, 'LineWidth', 3);
my_legend = [my_legend, {"BESS5"}];


myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$P_{\mathsf{elec}} (p.u. - S_{\mathrm{base}})$", "Interpreter", "latex");



subplot(2,4,5); % QELEC
hold on
QELEC1 = cellfun(@str2double, table2array(bspssepy_data(:,Gen1_index(4))));
QELEC2 = cellfun(@str2double, table2array(bspssepy_data(:,Gen2_index(4))));
QELEC3 = cellfun(@str2double, table2array(bspssepy_data(:,Gen3_index(4))));
BESS5_QELEC = cellfun(@str2double, table2array(bspssepy_data(:,BESS5_index(4))));


my_legend = {};
plot(time-1, QELEC1, 'LineWidth', 3);
my_legend = [my_legend, {"Gen1"}];
plot(time-1, QELEC2, 'LineWidth', 3);
my_legend = [my_legend, {"Gen2"}];
plot(time-1, QELEC3, 'LineWidth', 3);
my_legend = [my_legend, {"Gen3"}];
plot(time-1, BESS5_QELEC, 'LineWidth', 3);
my_legend = [my_legend, {"BESS5"}];

myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$Q_{\mathsf{elec}} (p.u. - S_{\mathrm{base}})$", "Interpreter", "latex");


subplot(2,4,6); % PMECH
hold on
PMECH1 = cellfun(@str2double, table2array(bspssepy_data(:,Gen1_index(5))));
PMECH2 = cellfun(@str2double, table2array(bspssepy_data(:,Gen2_index(5))));
PMECH3 = cellfun(@str2double, table2array(bspssepy_data(:,Gen3_index(5))));

my_legend = {};
plot(time-1, PMECH1, 'LineWidth', 3);
my_legend = [my_legend, {"Gen1"}];
plot(time-1, PMECH2, 'LineWidth', 3);
my_legend = [my_legend, {"Gen2"}];
plot(time-1, PMECH3, 'LineWidth', 3);
my_legend = [my_legend, {"Gen3"}];


myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$P_{\mathsf{m}} (p.u. - S_{\mathrm{m}})$", "Interpreter", "latex");





subplot(2,4,7); % FREQ
hold on

my_legend = {};
plot(time-1, freq_nan(:,1).*60, 'LineWidth',3);
my_legend = [my_legend, {"Gen1"}];
plot(time-1, freq_nan(:,2).*60, 'LineWidth',2);
my_legend = [my_legend, {"Gen2"}];
plot(time-1, freq_nan(:,3).*60);
my_legend = [my_legend, {"Gen3"}];
plot(time-1, freq_nan(:,4).*60);
my_legend = [my_legend, {"BESS5"}];



myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$f (Hz)$", "Interpreter", "latex");




subplot(2,4,4); % SOC
hold on
SOC_index = find(endsWith(bspssepy_data.Properties.VariableNames, 'residual energy', 'IgnoreCase',true));
SOC = cellfun(@str2double, table2array(bspssepy_data(:,SOC_index(1))));

my_legend = {};
plot(time-1, SOC, 'LineWidth', 3);
my_legend = [my_legend, {"BESS5 SOC"}];


myleg = legend(my_legend, "location", "best");

myleg.NumColumns = 1;
myleg.IconColumnWidth = 8;

grid on;

xlabel("$t [k]$", "Interpreter", "latex");
ylabel("$SOC [p.u.]$", "Interpreter", "latex");


%% Plotting MATLAB Simulation output for comparison

MATFile = "I:\Work\Research\Control & Power Systems\JWSP Research\HONI Project\Files From Harry\5 Jun 2025 - MATLAB BESS Integration\250529_ESS_in_frequency\250529_ESS_in_frequency\HarryPlotData30-Jun-2025.mat";


HarryPlotData = load(MATFile);

x = HarryPlotData.x;
y = HarryPlotData.y;
myColors = HarryPlotData.myColors;
numG = HarryPlotData.numG;
y1 = HarryPlotData.y1;
time = HarryPlotData.time;
freq_limit = HarryPlotData.freq_limit;
demand = HarryPlotData.demand;
numD = HarryPlotData.numD;
loads = HarryPlotData.loads;
stepsize = HarryPlotData.stepsize;
offline = HarryPlotData.offline;
crank = HarryPlotData.crank;
ramp = HarryPlotData.ramp;
online = HarryPlotData.online;

x = (max(y1(:,1)) - min(y1(:,1)))/20 * -((1:numG) - (numG+1)/2) + max(y1(:,1)) + 0.01;
y = [offline, crank, ramp, online];

figure(3)
yyaxis right
bargraph = barh(x,y(:,1:4), "stacked");
myColors = [0.8 0.8 0.8; 1 0 0; 1 1 0; 0 1 0];
for i = 1:4
    bargraph(i).FaceColor = 'flat';
    bargraph(i).CData = myColors(i,:);
    bargraph(i).BarWidth = 1;
end
yticks(sort(x))
yticklabels("Gen " + string(numG:-1:1))
ylim([min(y1(:,1)) - 0.01, max(x)+0.1])

xline(loads,"-","D" + string(1:numD) + " " + string(100 * demand(:,2))' + "MW","LineStyle","--","LabelVerticalAlignment","bottom");
hold on
yyaxis left
plot(time/stepsize, y1(:,1))
ylim([min(y1(:,1)) - 0.8, max(x) + 0.8])
yline(-60*freq_limit,"-","wlim","LineStyle","--","Color","red")
grid minor
xlabel("Timestep number")
ylabel("System Frequency [Hz]")




hold on
opts = delimitedTextImportOptions('DataLines',3,VariableNamesLine=2,VariableNamingRule='preserve');
bspssepy_data = readtable(csv_file ,opts,"ReadVariableNames", true);


freq_index = find(startsWith(bspssepy_data.Properties.VariableNames, 'freq', 'IgnoreCase',true));

freq = cellfun(@str2double, table2array(bspssepy_data(:,freq_index)));

[~, i_freq_avg] = max(abs(freq) > 0.00000001,[],1);

freq_mask = bsxfun(@gt, (1:size(freq,1))', i_freq_avg);
freq_nan = freq;
freq_nan(~freq_mask) = NaN;
avg_freq = mean(freq_nan,2, 'omitnan');
avg_freq(isnan(avg_freq)) = 0;

% convert freq to hz
avg_freq = avg_freq.*60;

time_index = find(startsWith(bspssepy_data.Properties.VariableNames, 'time', 'IgnoreCase',true));
time = cellfun(@str2double, table2array(bspssepy_data(:,time_index)));

% convert time to mins
time = time./60;

% convert time to "timestep number"
time = time./2;

plot(time-1, avg_freq,'-m',  'LineWidth',2)



% avg_freq(:) = mean([])
% plot()




hold off


