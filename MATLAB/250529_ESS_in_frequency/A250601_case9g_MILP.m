%% Getting System parameters from the casefile

mpc = case9g_newmodel_ESS; % load the case here
baseMVA = mpc.baseMVA; % set base MVA from the case
matY = makeYbus(mpc); % admittance matrix
matG = real(matY);
matB = imag(matY); % currently only reactance matrix is used in PF

numB = mpc.bus(end,1); % # of buses
numL = length(mpc.branch(:,1)); % # of lines
demand = mpc.demand; % list of demand lumps
demand(:,2) = demand(:,2) / baseMVA;
genprops = mpc.gen(:,[1, 4:6]); % gen properties (cranking, ramping)
genprops(:,2) = genprops(:,2) / baseMVA;
gendy = mpc.gendy;  % dynamic generator data

numD  = length(demand(:,1)); % # of demand lumps
numG = length(mpc.gen(:,1)); % # of all generators, first one is BSU

matDtoB = zeros(numB, numD); % demand to bus adjacency matrix
for i = 1: numD
    matDtoB(demand(i, 1), i) = 1;
end

matGtoB = zeros(numB, numG); % generator to bus adjacency matrix
for i = 1: numG
    matGtoB(mpc.gen(i, 1), i) = 1;
end

matAdj = makeIncidence(mpc); % network adjacency matrix
matLtoB = abs(matAdj)'; % maps lines to buses
matBtoL = transpose(matLtoB); % maps buses to lines
frombus = zeros(numL, 1); % to-bus indices
tobus = zeros(numL, 1); % from-bus indiced
for i = 1:numL
    frombus(i) = find(matAdj(i,:) == 1);
    tobus(i) = find(matAdj(i,:) == -1);
end

% generator min and max power outputs
genMax = mpc.gen(:, 2) / baseMVA;
genMin = mpc.gen(:, 3) / baseMVA;

% generator critical times
genTMax = mpc.gen(:, 7);
genTMin = mpc.gen(:, 8);
genTDead = mpc.gen(:, 9);

% line ratings
PLmax = mpc.branch(:,6) / baseMVA;

T = 60; % # of total timesteps
t = 10; % # of timesteps to look ahead
t_use = 1; % # of timesteps/actions that carry over to the next iteration. t_use <= t

T_solved = 0; % How many steps have been solved, updated at the end of each iteration

ramprate = genMax .* genprops(:, 4) / 100; % genprops(:, 4) gives ramp rate in %max/minute

matGcrank = zeros(T + t, T + t,numG-1); % size depends on how many steps to look ahead
for i = 1:(numG - 1)
    matGcrank(:,:,i) = eye(T + t) - diag(ones(T + t-genprops(i+1,3),1),min(genprops(i+1,3), T + t));
end

ramptime = ceil(genMin./ramprate);

matGramp = zeros(T + t, T + t,numG-1); % size depends on how many steps to look ahead
for i = 1:(numG - 1)
    matGramp(:,:,i) = diag(ones(T + t - genprops(i+1,3), 1),min(genprops(i+1,3), T + t)) ...
        - diag(ones(T + t - ramptime(i+1) - genprops(i+1,3),1),min(genprops(i+1,3) + ramptime(i+1), T + t));
end

% ESSVREs
numE = length(mpc.ess(:,1)); % # of ess units
essMax = mpc.ess(:,2) / baseMVA;
PeMax = mpc.ess(:,3) / baseMVA;
eta_cnv = mpc.ess(:,4); % conversion efficiency of ESS
eta_sto = mpc.ess(:,5); % energy density radio of ESS
tk = 1; % length of each step determines the energy unit

matEtoB = zeros(numB, numE); % ESS to bus adjacency matrix
for i = 1: numE
    matEtoB(mpc.ess(i, 1), i) = 1;
end

%% Initializing other variables

H = 0; % System-wide inertia
alpha = 0; % Per-unit capacities of generators, zero if offline
PL_max0 = 0; % maximum load pickup size of next steps
wlim = freq_limit;  % set frequency limit in p.u.
D = 0; % currently not considering damping

%ESSVRE
tau = mpc.ess(:, 6);

% Defining big-M values
M1 = max(abs(matB .* (1 - eye(numB))),[],'all') * pi /2 ;
M2 = PLmax;
M3 = pi/2;
M4 = genprops(:,2) + genMin;
M5 = genprops(:,2) + genMax;
M6 = max(genprops(:,2) + genMin, genMax + ramprate); %%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
M7 = ramptime .* ramprate;
M8 = (1+ramptime).*ramprate;
M9 = genprops(:,2) + ramprate;
M10 = genMin + ramprate/2;

%% Problem Formulation

% initial conditions
initL = zeros(numL, 1);
initB = [1; zeros(numB -1, 1)];
initD = zeros(numD, 1);
initG = [1; zeros(numG -1, 1)];
init_theta = [];
init_PL = [];
init_PG = [];
init_PGramp = [];
initGcrank = [0; initG(2:end)];
initGramp = [0; initG(2:end)];

%ESSVRE
initE = zeros(numE ,1); % for the binary variable binE
initEin = zeros(numE ,1); % for the binary variable binEin
initEout = zeros(numE ,1); % for the binary variable binEout
init_SOC = [0.2]; % for the continuous variable sdpSOC
init_Pein = zeros(numE ,1); % for the continuous variable sdpPein
init_Peout = zeros(numE ,1); % for the continuous variable sdpPeout

% init_Pvre = [];

while T_solved < T % MAIN LOOP

% Initializing binvars
binL = [initL, binvar(numL, t, 'full')]; % status of Lines
binB = [initB, binvar(numB, t, 'full')]; % status of buses
% binB(1,:) = ones(1, T + 1); % Bus 1 is slack, always active
binD = [initD, binvar(numD, t, 'full')]; % status of loads
binG = [initG, [ones(1,t); binvar(numG - 1, t, 'full')]]; % status of ALL generators, first row is the BSU
binGcrank = [initGcrank, [zeros(1,t); binvar(numG-1, t, 'full')]];
binGramp = [initGramp, [zeros(1,t); binvar(numG-1, t, 'full')]];

%ESSVRE
binE = [initE, binvar(numE, t, 'full')]; % indicator for whether ESS is online
binEin = [initEin, binvar(numE, t, 'full')]; % indicator of whether ESS is charging
binEout = [initEout, binvar(numE, t, 'full')]; % indicator of whether ESS is discharging 

binLcons = [];
binBcons = [];
binDcons = [];
binGcons = [];

%ESSVRE
binEcons = [];

for k = (T_solved+1): (T_solved + t)
    binLcons = [binLcons, (binL(:, k+1) - binL(:, k) >= zeros(numL,1)):['Stay on ' num2str(k)]]; % lines stay on
    binLcons = [binLcons, (sum(binL(:, k+1) - binL(:, k)) <= 1):['One per step ' num2str(k)]]; % turn on at most one line per step
    binBcons = [binBcons, (binB(:, k+1) - binB(:, k) >= zeros(numB,1)):['Stay on ' num2str(k)]]; % buses stay on
    binDcons = [binDcons, (binD( :, k+1) - binD(:, k) >= zeros(numD,1)):['Stay on ' num2str(k)]]; % loads stay on
    binDcons = [binDcons, (sum(binD(:, k+1) - binD(:, k)) <= 1):['One per step ' num2str(k)]]; % turn on at most one load per step
    binGcons = [binGcons, (binG(:, k+1) - binG(:, k) >= zeros(numG,1)):['Stay on ' num2str(k)]]; % GENs stay on
    binGcons = [binGcons, (sum(binG(:, k+1) - binG(:, k)) <= 1):['One per step ' num2str(k)]]; % turn on at most one GEN per step

    %ESSVRE
    binEcons = [binEcons, (binE(:, k+1) - binE(:, k) >= zeros(numE,1)):['Stay on ' num2str(k)]]; % ESS stay on

%     binGcons = [binGcons, sum([(binG(:, k+1) - binG(:, k)); (binL(:, k+1) - binL(:, k))]) <= 1]; % turn at most one NBSU OR one line on per step    
end

for k = max(1,T_solved - 1): (T_solved + t-2)
    binLcons = [binLcons, (sum(binL(:, k+1) - binL(:, k)) + sum(binL(:, k+2) - binL(:, k+1)) <= 1)]; % Cannot pickup line if previous step picked up one
end

% Initializing sdpvars
% sdpV = [1.04 * ones(1, T); sdpvar(numB - 1, T)]; % Voltages at all buses
sdptheta = [init_theta, [zeros(1, t); sdpvar(numB - 1, t, 'full')]]; % Phases at all buses
sdpPL = [init_PL, sdpvar(numL, t, 'full')]; % P line flows seen from From buses
sdpPG = [init_PG, sdpvar(numG, t, 'full')]; % Gen output at all buses
sdpPGramp = [init_PGramp, sdpvar(numG, t + 1, 'full')];

%ESSVRE
sdpSOC = [init_SOC, sdpvar(numE, t, 'full')];
sdpPein = [init_Pein, sdpvar(numE, t, 'full')];
sdpPeout = [init_Peout, sdpvar(numE, t, 'full')];
% sdpPvre = [init_Pvre, sdpvar(numE, t, 'full')];

Pbalancecons = [];
sdpPLcons = [];
sdpPGcons = [];
sdpthetacons = [];
binGstartcons = [];
binGreservecons = [];
binGtimecons = [];
sdpfreqcons = [];

%ESSVRE
sdpESScons = [];
% sdpVREcons = [];

% Update inertia, alpha, and frequency constraints
[H, alpha, PL_max0, gradESS] = F250601_H_update(H, alpha, T_solved + 1, initG, mpc, T, t, wlim, tau);

% Placing constraints for the MILP
for k = (T_solved + 1): (T_solved + t)
    %ESSVRE
    sdpfreqcons = [sdpfreqcons, (demand(:,2)' * (binD(:,k+1) - binD(:,k)) + genprops(:,2)' * (binG(:,k+1) - binG(:,k)) <= PL_max0(k) + gradESS(k)' * (diag(eta_cnv)*(sdpPeout(:,k+1)-sdpPeout(:,k)) - diag(eta_cnv)^-1*(sdpPein(:,k+1)-sdpPein(:,k))))]; % net load change is less than freqcon
%     sdpfreqcons = [sdpfreqcons, (genprops(:,2)' * (binG(:,k+1) - binG(:,k)) <= PL_max(k+1))];

    for i = 1:numL
%         sdpPL(i, k) =  matB(frombus(i), tobus(i)) * (sdptheta(frombus(i), k) - sdptheta(tobus(i),k)); % Line flows
        sdpthetacons = [sdpthetacons, (-M1*(1-binL(i, k+1)) <= (sdpPL(i, k) -matB(frombus(i), tobus(i)) * (sdptheta(frombus(i), k) - sdptheta(tobus(i),k))) <= M1*(1-binL(i, k+1))):['Flow logic bus ' num2str(i)]];
        % bus is on if an adjacent line is on
        binBcons = [binBcons, (matLtoB(:,i) * binL(i,k+1) <= binB(:,k+1)):['BtoL logic ON bus ' num2str(i)]];
    end
end

for i = 2:numG % critical time constraints on NBSUs, hence starting at 2
    binGcrank(i,2:end) = binG(i,2:end) * matGcrank(1:(T_solved + t),1:(T_solved + t),i-1); % cranking timesteps 1, else 0
    binGramp(i,2:end) = binG(i,2:end) * matGramp(1:(T_solved + t),1:(T_solved + t),i-1); % ramping timesteps 1, else 0

    if genTMin(i) > 0 % if equal to zero, there s no TMin enforced on gen i
        binGtimecons = [binGtimecons, (binG(i, min(genTMin(i), T_solved + t)) == 0):['TMin gen ' num2str(i)]];
    end

    if ~isinf(genTMax(i)) % if equal to zero, there s no TMax enforced on gen i
        if (T_solved + t) >= genTMax(i) % gen must start before TMax or be poisoned out for TDead
            binGtimecons = [binGtimecons, (binG(i, genTMax(i)) * ones(1, min(genTDead(i), T_solved + t - genTMax(i))) >= ...
                binG(i, (genTMax(i) + 1):(genTMax(i) + min(genTDead(i), T_solved + t - genTMax(i)))))]; % :['TMax gen ' num2str(i)]]
        end
    end
end

binGop = binG - binGcrank - binGramp;

for k = (T_solved + 1): (T_solved + t)
    % bus is off if all adjacent lines are off
    binBcons = [binBcons, (binB(:,k+1) - matLtoB * binL(:,k+1) <= 0):['BtoL logic OFF']];
    % line pickups most connect to an already active bus
    binBcons = [binBcons, (binL(:,k+1) <= matBtoL * binB(:,k)):['Line connect ' num2str(k)]];
%     binBcons = [binBcons, binB(:,k+1) - matDtoB * binD(:,k+1) <= 0]; % bus cannot be on if no demand is on
    Pbalancecons = [Pbalancecons, (matGtoB * sdpPG(:, k) - matDtoB * (binD(:, k+1) .* demand(:, 2)) - transpose(matAdj) * sdpPL(:, k) + matEtoB*(diag(eta_cnv)*sdpPeout(:,k+1) - diag(eta_cnv)^-1*sdpPein(:,k+1))== zeros(numB,1)):['Pbalance ' num2str(k)]];
    % flow is zero if the line is off
    sdpPLcons = [sdpPLcons, (-M2.*binL(:, k+1) <= sdpPL(:, k) <= M2.*binL(:, k+1)):['Flow logic ' num2str(k)]];
    % phase at offline buses is zero
    sdpthetacons = [sdpthetacons, (-M3*binB(:, k+1) <= sdptheta(:, k) <= M3*binB(:, k+1)):['Bus logic ' num2str(k)]];
    % sdpthetacons = [sdpthetacons, (sdptheta(1, k) == 0)];
    % NBSU pickups must be after bus is energized
    binGcons = [binGcons, (matGtoB * binG(:,k+1) <= binB(:,k)):['Bus logic ' num2str(k)]];
    sdpPGcons = [sdpPGcons, (genMin(1) <= sdpPG(1, k) <= genMax(1)):['BSU bounds ' num2str(k)]]; % BSU generator limits
    
    % enforcing crank and ramp characteristic
    binGstartcons = [binGstartcons, (-M4.*(binGcrank(:,k+1) + binGramp(:,k+1)) + binG(:, k+1) .* genMin <= sdpPG(:, k) <= binG(:, k+1) .* genMax + M4.*(binGcrank(:,k+1) + binGramp(:,k+1))):['Crank-Ramp A ' num2str(k)]]; % GEN limits
    binGstartcons = [binGstartcons, (-M5.*(1 - binGcrank(:, k+1)) <= sdpPG(:, k) + genprops(:,2) <= M5.*(1 - binGcrank(:, k+1))):['Crank-Ramp B ' num2str(k)]]; % GEN limits
    binGstartcons = [binGstartcons, (-M6.*(1 - binGramp(:, k+1)) <= sdpPG(:, k) - sdpPGramp(:, k+1) <= M6.*(1 - binGramp(:, k+1))):['Crank-Ramp C ' num2str(k)]]; % GEN limits

    % setting the ramping reference P_ref
    binGstartcons = [binGstartcons, (-M7 .* binGramp(:,k) <= sdpPGramp(:, k) + ramprate/2 <= M7 .* binGramp(:,k)):['Ramp ref A ' num2str(k)]];
    binGstartcons = [binGstartcons, (-M8 .* (1 - binGramp(:,k+1)) <= sdpPGramp(:, k+1) - sdpPGramp(:, k) - ramprate <= M8 .* (1 - binGramp(:,k+1))):['Ramp ref B ' num2str(k)]];

    % dynamic reserve conditions 
%     binGreservecons = [binGreservecons, (binGop(:,k+1) .* genMax(2:end) <= ones(numG-1, numG) * ([1; binGop(:,k+1)] .* genMax - sdpPG(:,k))):['Gen reserve ' num2str(k)]];
      binGreservecons = [binGreservecons, (0.95 * (genMax' * binGop(:,k+1)) - genprops(:,2)' * binGcrank(:,k+1) - demand(:,2)' * binD(:,k+1))>= 0];

    %ESSVRE
    sdpESScons = [sdpESScons, (matEtoB * binE(:,k+1) <= binB(:,k+1)):['ESS logic ' num2str(k)]]; % ESS can turn on if bus is turned on
    sdpESScons = [sdpESScons, (binEin(:,k+1) + binEout(:,k+1) <= binE(:,k+1))]; % Cannot charge or discharge when ESS off, can charge OR discharge when ESS on
    sdpESScons = [sdpESScons, (0 <= sdpPein(:,k+1) <= 55 * binEin(:,k+1))]; % Coupling binEin with sdpPein
    sdpESScons = [sdpESScons, (0 <= sdpPeout(:,k+1) <= 55 * binEout(:,k+1))]; % Coupling binEin with sdpPein
    sdpESScons = [sdpESScons, (sdpSOC(:,k+1) == sdpSOC(:,k) + tk * (diag(eta_sto)*sdpPein(:,k+1) - diag(eta_sto)^-1 * sdpPeout(:,k+1)))]; % SOC update equation
    sdpESScons = [sdpESScons, (0 <= sdpSOC(:,k+1) <= essMax)]; % limiting the maximum energy stored
    sdpESScons = [sdpESScons, (-PeMax <= diag(eta_cnv)*sdpPeout(:,k+1) - diag(eta_cnv)^-1*sdpPein(:,k+1) <= PeMax)]; % limiting the maximum power to/from the grid
end

if T_solved > 0
        % ramping reference P_ref first the first timestep
        binGstartcons = [binGstartcons, (-M8 .* (1 - binGramp(:,T_solved+1)) <= sdpPGramp(:, T_solved+1) - sdpPGramp(:, T_solved) - ramprate <= M8 .* (1 - binGramp(:,T_solved+1))):['Ramp ref B ' num2str(k)]];
        
    for k = T_solved:(T_solved + t - 1)
        %ramp rate bounds after ramping phase
        binGcons = [binGcons, (-(ramprate + M9 .*(1 - binGop(:,k+2))) <= (sdpPG(:,k+1) - sdpPG(:,k)) <= ramprate + M9 .*(1 - binGop(:,k+2))):['Output RoC bound' num2str(k)]];
    end
end 
binGstartcons = [binGstartcons, (-M10 .* binGramp(:,T_solved + t + 1) <= sdpPGramp(:, T_solved + t + 1) + ramprate/2 <= M10 .* binGramp(:,T_solved + t + 1)):['Ramp ref last']]; % for the last step, otherwise binGramp returns NaN at the last step


%% Objective Function

% Energy Objective
% obj = - sum(binD' * diag(demand(:,3)) * demand(:, 2)) * 100 - sum(binL' * ones(numL,1)) - sum(binG' * ones(numG -1,1));
% Generator Objective
obj = -10 * sum(binD' * diag(demand(:,3)) * demand(:, 2)) - sum(binL' * ones(numL,1)) - 100 * sum(binG' * ones(numG,1)) - sum(binE);

% Two-stage Objective
% if sum(initG(:, end)) ~= numG-1
%     obj = - sum(binL' * ones(numL,1)) - 100* sum(binG' * ones(numG -1,1)); % priority on gens until all are active
% else
%     obj = - sum(binD' * diag(demand(:,3)) * demand(:, 2)) * 100 - sum(binL' * ones(numL,1)); % priority on load after all gens active
% end

%% Solver
options = sdpsettings('solver','gurobi','verbose',0);
result = optimize([binLcons, binBcons, binDcons, sdpPLcons, sdpPGcons, sdpthetacons, Pbalancecons, binGcons, binGstartcons, sdpfreqcons, binGreservecons, binEcons, sdpESScons], obj, options);
% Not used: , binGtimecons 

% convert sdpvar to double
binD = value(round(binD));
binL = value(round(binL));
binB = value(round(binB));
binG = value(round(binG));
binGcrank = value(round(binGcrank));
binGramp = value(round(binGramp));
binGop = value(binGop);
obj = value(obj);
sdpPL = value(sdpPL);
sdptheta = value(sdptheta);
sdpPG = value(sdpPG);
sdpPGramp = value(sdpPGramp);

%ESSVRE
binE = value(round(binE));
binEin = value(round(binEin));
binEout = value(round(binEout));
sdpSOC = value(sdpSOC);
sdpPein = value(sdpPein);
sdpPeout = value(sdpPeout);

% initialize next step with first timestep of new solution
initD = binD(:, 1: (T_solved + t_use + 1));
initL = binL(:, 1: (T_solved + t_use + 1));
initB = binB(:, 1: (T_solved + t_use + 1));
initG = binG(:, 1: (T_solved + t_use + 1));
initGcrank = binGcrank(:, 1: (T_solved + t_use + 1));
initGramp = binGramp(:, 1: (T_solved + t_use + 1));
init_PL = sdpPL(:, 1:(T_solved + t_use));
init_theta = sdptheta(:, 1:(T_solved + t_use));
init_PG = sdpPG(:, 1:(T_solved + t_use));
init_PGramp = sdpPGramp(:, 1:(T_solved + t_use));

%ESSVRE
initE = binE(:,1: (T_solved + t_use + 1)); % for the binary variable binE
initEin = binEin(:,1: (T_solved + t_use + 1)); % for the binary variable binEin
initEout = binEout(:,1: (T_solved + t_use + 1)); % for the binary variable binEout
init_SOC = sdpSOC(:, 1:(T_solved + t_use + 1)); % for the continuous variable sdpSOC
init_Pein = sdpPein(:, 1:(T_solved + t_use + 1)); % for the continuous variable sdpPein
init_Peout = sdpPeout(:, 1:(T_solved + t_use + 1)); % for the continuous variable sdpPeout

T_solved = T_solved + t_use;

disp("MILP: Running " + T_solved + " of " + T + " timesteps...")
yalmip clear
end

%% Truncate at
%% Analysis
sequence = cell(7, T);
sequence(:,:) = {0};
% label the sequence of actions

for k = 1:T
    tag = "";
    if ~isempty(find(binL(:,k+1) - binL(:,k)))
        tag = tag + "L";
        sequence{2,k} = find(binL(:,k+1) - binL(:,k));
    end 
    if ~isempty(find(binB(:,k+1) - binB(:,k)))
        tag = tag + "B";
        sequence{3,k} = find(binB(:,k+1) - binB(:,k));
    end 
    if ~isempty(find(binD(:,k+1) - binD(:,k)))
        tag = tag + "D";
        sequence{4,k} = find(binD(:,k+1) - binD(:,k));
    end
    if ~isempty(find(binG(:,k+1) - binG(:,k)))
        tag = tag + "G";
        sequence{5,k} = genprops(find(binG(:,k+1) - binG(:,k)),1);
    end
    if ~isempty(find(binGcrank(:,k+1)))
        sequence{6,k} =  genprops(find(binGcrank(:,k+1)));
    end
    if ~isempty(find(binGramp(:,k+1)))
        sequence{7,k} =  genprops(find(binGramp(:,k+1)));
    end
    sequence{1,k} = tag;
end
disp(sequence)

% data = [diag(demand(:,2))* binD(:,2:end); sdpPG; binGcrank(:,2:end); binGramp(:,2:end); binGop(:,2:end); PL_max(:,2:end)];
% writematrix(data,"MILP_output.xlsx","Range","B2","WriteMode","inplace")

return
%% Plotting

% a = [0 0 0.5 0.7 0.9 1];
% b = [0 0.2 0.4 0.4 0.9 1];
% t = 1:6;
% plot(t,b,'r-o',t,a,'b-o')



plot(binD' * demand(:, 2))