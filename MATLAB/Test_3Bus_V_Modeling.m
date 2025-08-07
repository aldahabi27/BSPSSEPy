%%
%==========================================================================
% LPAC Affine Approximation Power Flow (P and Q Solved)
% 6 August 2025 | Ilyas Farhat | HONI Project
%==========================================================================

clear; clc; close all;

%%-----------------------------
% Step 1: Define MATPOWER Case
%------------------------------
mpc.version = '2';
mpc.baseMVA = 100;

mpc.bus = [
    1   3   0     0     0  0   1  1.0   0   230  1  1.1  0.9;  % Slack
    2   1   0     0     0  0   1  1.0   0   230  1  1.1  0.9;
    3   1   4     0.4   0  0   1  1.0   0   230  1  1.1  0.9;
];

mpc.gen = [
    1   60   0   0   0;  % Generator at bus 1
];

mpc.branch = [
    1   2   0     0.1   0    250 250 250  0  0  1  -360 360  1;
    2   3   0.01  0.2   0.8  250 250 250  0  0  1  -360 360  0;
];

%%-----------------------------
% Step 2: Build Ybus, G, B
%------------------------------
[ybus, ~, ~] = makeYbus(mpc);
ybus = full(ybus);
G = real(ybus);
B = imag(ybus);
nb = size(mpc.bus, 1);

%%-----------------------------
% Step 3: Define Power Injections
%------------------------------
P = zeros(nb,1); Q = zeros(nb,1);
P(mpc.gen(:,1)) = mpc.gen(:,3);
Q(mpc.gen(:,1)) = mpc.gen(:,4);
P = P - mpc.bus(:,3);  % Subtract Pd
Q = Q - mpc.bus(:,4);  % Subtract Qd

%%-----------------------------
% Step 4: LPAC Linear System Construction
%------------------------------
slack = find(mpc.bus(:,2) == 3);
non_slack = setdiff(1:nb, slack);
ns = length(non_slack);

% Initialize blocks
A_theta_P = zeros(nb, nb);
B_phi_P   = zeros(nb, nb);
A_theta_Q = zeros(nb, nb);
B_phi_Q   = zeros(nb, nb);

% Fill matrices
for i = 1:nb
    for k = 1:nb
        if i ~= k
            % ΔP
            A_theta_P(i,i) = A_theta_P(i,i) + B(i,k);
            A_theta_P(i,k) = A_theta_P(i,k) - B(i,k);
            B_phi_P(i,i)   = B_phi_P(i,i) + G(i,k);
            B_phi_P(i,k)   = B_phi_P(i,k) + G(i,k);

            % ΔQ
            A_theta_Q(i,i) = A_theta_Q(i,i) + G(i,k);
            A_theta_Q(i,k) = A_theta_Q(i,k) - G(i,k);
            B_phi_Q(i,i)   = B_phi_Q(i,i) - B(i,k);
            B_phi_Q(i,k)   = B_phi_Q(i,k) - B(i,k);
        end
    end
end

% Combine into one big system (remove slack rows and columns)
A_big = [ A_theta_P(non_slack, non_slack), B_phi_P(non_slack, non_slack);
          A_theta_Q(non_slack, non_slack), B_phi_Q(non_slack, non_slack) ];

rhs_big = [P(non_slack); Q(non_slack)];

% Solve the system
x = A_big \ rhs_big;
theta = zeros(nb,1);
phi   = zeros(nb,1);

theta(non_slack) = x(1:ns);
phi(non_slack)   = x(ns+1:end);
V = 1 + phi;

%%-----------------------------
% Step 5: Display Results
%------------------------------
fprintf('\n==== LPAC Voltage Solution with P & Q ====\n');
fprintf('Bus |   V(pu)   | Theta(rad) |   P(MW)   |  Q(MVAr)\n');
fprintf('---------------------------------------------------\n');
for i = 1:nb
    fprintf('%3d |  %7.4f  |   %8.4f |  %8.3f |  %8.3f\n', ...
        i, V(i), theta(i), P(i), Q(i));
end


%%
%==========================================================================
% LPAC Affine Approximation Power Flow (3-Bus Example)
% 5 August 2025 | Ilyas Farhat | HONI Project
%==========================================================================

clear; clc; close all;

%%-----------------------------
% Step 1: Define MATPOWER Case
%------------------------------
mpc.version = '2';
mpc.baseMVA = 100;

% Bus data: bus_i, type, Pd, Qd, Gs, Bs, area, Vm, Va, baseKV, zone, Vmax, Vmin
mpc.bus = [
    1   3   0     0     0  0   1  1.0   0   230  1  1.1  0.9;  % Slack
    2   1   0     0     0  0   1  1.0   0   230  1  1.1  0.9;
    3   1   4     0.4   0  0   1  1.0   0   230  1  1.1  0.9;
];

% Generator data: bus, Pmax, Pmin, Pgen, Qgen
mpc.gen = [
    1   60   0   0   0;  % Generator at bus 1
];

% Branch data: fbus, tbus, r, x, b, rateA, rateB, rateC, ratio, angle, status, angmin, angmax, isTransformer
mpc.branch = [
    1   2   0     0.1   0    250 250 250  0  0  1  -360 360  1;
    2   3   0.01  0.2   0.8  250 250 250  0  0  1  -360 360  0;
];

% Demand data: bus, load, weight (not used in this model)
mpc.demand = [
    3   4   1;
];

%%-----------------------------
% Step 2: Build Ybus, G, B
%------------------------------
[ybus, ~, ~] = makeYbus(mpc);
ybus = full(ybus);
B = imag(ybus);
G = real(ybus);

nb = size(mpc.bus, 1);

%%-----------------------------
% Step 3: Define Power Injections (P, Q)
%------------------------------
P = zeros(nb,1); Q = zeros(nb,1);

% Injected power from generators
P(mpc.gen(:,1)) = mpc.gen(:,3);
Q(mpc.gen(:,1)) = mpc.gen(:,4);

% Subtract loads
P = P - mpc.bus(:,3);
Q = Q - mpc.bus(:,4);

%%-----------------------------
% Step 4: LPAC Initialization
%------------------------------
phi   = zeros(nb,1);  % Voltage magnitude deviation
theta = zeros(nb,1);  % Voltage angle
V     = 1 + phi;

%%-----------------------------
% Step 5: Build Linear System
%------------------------------
slack = find(mpc.bus(:,2) == 3);
non_slack = setdiff(1:nb, slack);
ns = length(non_slack);

% Initialize matrices
A_theta = zeros(nb, nb);
B_phi   = zeros(nb, nb);

for i = 1:nb
    for k = 1:nb
        if i ~= k
            theta_ik = theta(i) - theta(k);
            A_theta(i,i) = A_theta(i,i) + B(i,k);        % θ_i coefficient
            A_theta(i,k) = A_theta(i,k) - B(i,k);        % -θ_k coefficient
            B_phi(i,i)   = B_phi(i,i) + G(i,k);          % φ_i
            B_phi(i,k)   = B_phi(i,k) + G(i,k);          % φ_k
        end
    end
end

% Eliminate slack bus
A_red = [A_theta(non_slack, non_slack), B_phi(non_slack, non_slack)];
rhs   = P(non_slack);

% Solve [theta; phi]
x = A_red \ rhs;

% Assign solutions
theta(non_slack) = x(1:ns);
phi(non_slack)   = x(ns+1:end);
V = 1 + phi;

%%-----------------------------
% Step 6: Display Results
%------------------------------
fprintf('\n==== LPAC Voltage Solution ====\n');
fprintf('Bus |   V(pu)   | Theta(rad) |   P(MW)   |  Q(MVAr)\n');
fprintf('---------------------------------------------------\n');
for i = 1:nb
    fprintf('%3d |  %7.4f  |   %8.4f |  %8.3f |  %8.3f\n', ...
        i, V(i), theta(i), P(i), Q(i));
end


%%

% 3 Bus   Power flow data
clear
clc
close all

%   Please see CASEFORMAT for details on the case file format.
%
%   Based on data from p. 70 of:
%
%   Chow, J. H., editor. Time-Scale Modeling of Dynamic Networks with
%   Applications to Power Systems. Springer-Verlag, 1982.
%   Part of the Lecture Notes in Control and Information Sciences book
%   series (LNCIS, volume 46)
%
%   which in turn appears to come from:
%
%   R.P. Schulz, A.E. Turner and D.N. Ewart, "Long Term Power System
%   Dynamics," EPRI Report 90-7-0, Palo Alto, California, 1974.

%   MATPOWER

% MATPOWER Case Format : Version 2
mpc.version = '2';

%%-----  Power Flow Data  -----%%
% system MVA base
mpc.baseMVA = 100;

% bus data
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	    Va	baseKV	zone	Vmax	Vmin
mpc.bus = [
	1	    3	    0	0	0	0	1	    1	    0	230	    1	    1.1	    0.9;
	2	    1	    0	0	0	0	1	    1	    0	230	    1	    1.1	    0.9;
	3	    1	    4	0.4	0	0	1	    1	    0	230	    1	    1.1	    0.9;
];

% generator data
%	bus	P_max P_min P_c T_c r%/m T_max T_min T_dead
mpc.gen = [
	1	60	    0	0   0   20   inf    0   5;
];

% generator dynamics data
%	bus	H U0 T4 T5 T6 T7 K1 K3 K5 K7
% mpc.gendy = [
% 	1	5.55 0.2/60 0.2 0.1 0.12 0.15 0.4 0.2 0.2 0.2;
% 	2	4.33 0.2/60 0.2 0.1 0.12 0.15 0.4 0.2 0.2 0.2;
% 	3	3.35 0.1/60 0.2 0.1 0.12 0.15 0.4 0.2 0.2 0.2;
% ];

% branch data
%	fbus	tbus	r	    x	    b	    rateA	rateB	rateC	ratio	angle	status	angmin	angmax IsTransformer
mpc.branch = [
	1	    2	    0	    0.1	    0	    250	    250	    250	    0	    0	    1	    -360	360     1;
	2	    3	    0.01	0.2	    0.8	    250	    250	    250	    0	    0	    1	    -360	360     0;
];

%%-----  OPF Data  -----%%
% generator cost data
%	1	startup	shutdown	n	x1	y1	...	xn	yn
%	2	startup	shutdown	n	c(n-1)	...	c0
% mpc.gencost = [
% 	2	1500	0	3	0.11	5	150;
% 	2	2000	0	3	0.085	1.2	600;
% 	2	3000	0	3	0.1225	1	335;
% ];

% demand data
%           bus, load, weight
mpc.demand = [  3	4   1;];

% ESS data
%         bus   E_max   P_max  eta_cnv eta_sto tau(s)
% mpc.ess = [5    50      20     1       1       1];



[ybus, yf, yt] = makeYbus(mpc);

ybus = full(ybus)

B = imag(ybus);
G = real(ybus);
nb = size(mpc.bus, 1);
nl = size(mpc.branch, 1);

% Power Injections
P = zeros(nb,1); Q = zeros(nb,1);
P(mpc.gen(:,1)) = mpc.gen(:,2);
Q(mpc.gen(:,1)) = mpc.gen(:,3);
P(mpc.bus(:,1)) = P(mpc.bus(:,1)) - mpc.bus(:,3);   % subtract load Pd
Q(mpc.bus(:,1)) = Q(mpc.bus(:,1)) - mpc.bus(:,4);   % subtract load Qd

% Slack Bus: Fix θ1 = 0, V1 = 1
theta = zeros(nb,1);
V = ones(nb,1);

% LPAC Affine Approxmiation (cos ~ 1 and sin ~ theta_i - theta_j)
DP = zeros(nb,1);
DQ = zeros(nb,1);

phi = zeros(nb,1);  % voltage magnitude deviation
theta = zeros(nb,1);  % angle, already initialized
V = 1 + phi;          % voltage magnitude approximation

for i = 1:nb
    for k = 1:nb
        if i ~= k
            theta_ik = theta(i) - theta(k);
            DP(i) = DP(i) + (1 + phi(i) + phi(k)) * (G(i,k) + B(i,k) * theta_ik);
            DQ(i) = DQ(i) + (1 + phi(i) + phi(k)) * (G(i,k) * theta_ik - B(i,k));
        else
            % Diagonal term — typically:
            DP(i) = DP(i) + (2 * phi(i)) * G(i,i);  % from derivation (2Vi - 1)*Gii
            DQ(i) = DQ(i) + (2 * phi(i)) * (-B(i,i));  % similar logic
        end
    end
end



%%




% DC PF
B = imag(ybus);       % susceptance matrix
n_bus = size(B,1);
P = zeros(n_bus,1);   % initialize active power injections

% Define net real injections
P(1) = 4;     % generator at bus 1
P(3) = -4;    % load at bus 3

% Slack bus is bus 1 → fix angle to 0, remove row/col
B_red = B(2:end, 2:end);
P_red = P(2:end);

% Solve for θ
theta = zeros(n_bus, 1);
theta(2:end) = B_red \ P_red;


% Linear Q model

Q = zeros(n_bus,1);   % define known Q injections
Q(3) = -0.4;          % load Q at bus 3
Q(1) = 0.4;           % generator supplying 0.4 pu

b0 = zeros(n_bus,1);  % shunt susceptance at each bus (Bs column in mpc.bus)

% Add shunt from line charging B/2 at buses 2 and 3
% Branch 2–3 has b = 0.8 → 0.4 at each side
b0(2) = b0(2) + 0.4;
b0(3) = b0(3) + 0.4;

% Build coefficient matrix A such that A*V = Q + b0
A = zeros(n_bus);
for k = 1:n_bus
    for j = 1:n_bus
        if k ~= j
            A(k,j) = -abs(B(k,j));
        end
    end
    A(k,k) = -sum(A(k,:));
end

% Fix V(1) = 1 pu (slack)
A_red = A(2:end, 2:end);
rhs = Q(2:end) + b0(2:end) - A(2:end,1) * 1;

V = zeros(n_bus,1);
V(1) = 1;
V(2:end) = A_red \ rhs;


disp('   Bus      V(pu)     Theta(rad)     P(MW)     Q(MVAr)')
disp([ (1:n_bus)'   V        theta         P       Q ])



% LPAC modeling
% Extract susceptance (imag) and conductance (real)
B = imag(ybus);
G = real(ybus);

% Power injections (MW and MVAr)
P = zeros(n_bus,1);
Q = zeros(n_bus,1);
P(1) = 4;      % gen
P(3) = -4;     % load
Q(1) = 0.4;
Q(3) = -0.4;


% Slack: fix θ1 = 0, V1 = 1
theta = zeros(n_bus,1);
V = ones(n_bus,1);

% Affine approximation of voltage product term
V_prod_affine = @(Vi, Vj) 1 + (Vi - 1) + (Vj - 1);  % or Vi + Vj - 1

% Build B' and G' for θ (remove slack bus row/col)
B_theta = -G(2:end,2:end);
P_red = P(2:end);

% Solve for θ
theta(2:end) = B_theta \ P_red;

% Shunt susceptance (Bs column + line B/2)
b0 = zeros(n_bus,1);
for k = 1:size(mpc.branch,1)
    f = mpc.branch(k,1);
    t = mpc.branch(k,2);
    b = mpc.branch(k,5);
    b0(f) = b0(f) + b/2;
    b0(t) = b0(t) + b/2;
end

% Build LPAC voltage equation: Q = B*(V_i - V_j) + b0
A = zeros(n_bus);
for i = 1:n_bus
    for j = 1:n_bus
        if i ~= j
            A(i,j) = -B(i,j);
        end
    end
    A(i,i) = -sum(A(i,:));
end

% Fix V1 = 1
A_red = A(2:end, 2:end);
rhs = Q(2:end) + b0(2:end) - A(2:end,1) * 1;

V(1) = 1;
V(2:end) = A_red \ rhs;

disp('n   Bus      V(pu)     Theta(rad)     P(MW)     Q(MVAr)')
disp([ (1:n_bus)'   V        theta         P       Q ])



%%
% LPAC Power Flow for 3-Bus Test Case

% clear; clc;

%% Define System Base
baseMVA = 100;

%% Bus Data: [bus_i type Pd Qd Gs Bs area Vm Va baseKV zone Vmax Vmin]
bus = [
    1  3  0     0     0  0  1  1.0  0  230 1  1.1  0.9;
    2  1  0     0     0  0  1  1.0  0  230 1  1.1  0.9;
    3  1  4     0.4   0  0  1  1.0  0  230 1  1.1  0.9;
];

%% Generator Data
% [bus, Pg, Qg]
gen = [
    1, 4, 0.4;
];

%% Branch Data: [from to r x b]
branch = [
    1 2  0.01  0.1   0.0;
    2 3  0.01  0.2   0.8;
];

%% System size
nb = size(bus, 1);
nl = size(branch, 1);

%% Form Admittance Matrix Ybus
Y = zeros(nb, nb);
G = zeros(nb); B = zeros(nb);

for k = 1:nl
    i = branch(k,1);
    j = branch(k,2);
    r = branch(k,3);
    x = branch(k,4);
    b = branch(k,5);

    z = r + 1i*x;
    y = 1/z;
    b_shunt = 1i * b / 2;

    % Off-diagonal
    Y(i,j) = Y(i,j) - y;
    Y(j,i) = Y(j,i) - y;

    % Diagonal
    Y(i,i) = Y(i,i) + y + b_shunt;
    Y(j,j) = Y(j,j) + y + b_shunt;
end

G = real(Y);
B = imag(Y);

%% Power Injections
P = zeros(nb,1); Q = zeros(nb,1);
P(gen(:,1)) = gen(:,2);
Q(gen(:,1)) = gen(:,3);
P(bus(:,1)) = P(bus(:,1)) - bus(:,3);   % subtract load Pd
Q(bus(:,1)) = Q(bus(:,1)) - bus(:,4);   % subtract load Qd

%% Slack Bus: Fix θ1 = 0, V1 = 1
theta = zeros(nb,1);
V = ones(nb,1);

%% === 1. Real Power Flow Equation (LPAC)

% Affine approximation: cos ≈ 1, sin ≈ θ_i - θ_j
A_theta = zeros(nb);
for i = 1:nb
    for j = 1:nb
        if i ~= j
            A_theta(i,j) = -G(i,j);
            A_theta(i,i) = A_theta(i,i) + G(i,j);
        end
    end
end

% Remove slack row/col (bus 1)
A_theta_red = A_theta(2:end, 2:end);
P_red = P(2:end);
theta(2:end) = A_theta_red \ P_red;

%% === 2. Reactive Power Flow (LPAC with affine V_i V_j)

% Shunt susceptance
b0 = zeros(nb,1);
for k = 1:nl
    i = branch(k,1);
    j = branch(k,2);
    b = branch(k,5);
    b0(i) = b0(i) + b/2;
    b0(j) = b0(j) + b/2;
end

% Build A_V matrix for: Q = A_V * V + b0
A_V = zeros(nb);
for i = 1:nb
    for j = 1:nb
        if i ~= j
            A_V(i,j) = -B(i,j);
            A_V(i,i) = A_V(i,i) + B(i,j);
        end
    end
end

% Fix V1 = 1
A_V_red = A_V(2:end, 2:end);
rhs = Q(2:end) + b0(2:end) - A_V(2:end,1) * V(1);
V(2:end) = A_V_red \ rhs;

%% Display Results
fprintf('\n%-6s %-10s %-12s %-10s %-10s\n', 'Bus', 'V (pu)', 'Theta (rad)', 'P (MW)', 'Q (MVAr)');
for i = 1:nb
    fprintf('%-6d %-10.4f %-12.4f %-10.4f %-10.4f\n', i, V(i), theta(i), P(i), Q(i));
end
