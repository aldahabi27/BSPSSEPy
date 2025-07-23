function mpc = case9g_newmodel_ESS
%CASE9    Power flow data for 9 bus, 3 generator case.
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

%% MATPOWER Case Format : Version 2
mpc.version = '2';

%%-----  Power Flow Data  -----%%
%% system MVA base
mpc.baseMVA = 100;

%% bus data
%	bus_i	type	Pd	Qd	Gs	Bs	area	Vm	Va	baseKV	zone	Vmax	Vmin
mpc.bus = [
	1	3	0	0	0	0	1	1	0	345	1	1.1	0.9;
	2	1	10	10	0	0	1	1	0	345	1	1.1	0.9;
	3	1	40	10	0	0	1	1	0	345	1	1.1	0.9;
	4	1	25	10	0	0	1	1	0	345	1	1.1	0.9;
	5	1	20	10	0	0	1	1	0	345	1	1.1	0.9;
	6	1	30	10	0	0	1	1	0	345	1	1.1	0.9;
	7	1	10	35	0	0	1	1	0	345	1	1.1	0.9;
	8	1	30	10	0	0	1	1	0	345	1	1.1	0.9;
	9	1	60	20	0	0	1	1	0	345	1	1.1	0.9;
];

%% generator data
%	bus	P_max P_min P_c T_c r%/m T_max T_min T_dead
mpc.gen = [
	1	247.5	0	0   0   20   inf 0   5;
	2	192.0	38.4	9.6  30  20   6 0   5;
	3	128.0	25.6	3.84  20   10   inf 0   5;
];

%% generator dynamics data
%	bus	H U0 T4 T5 T6 T7 K1 K3 K5 K7
mpc.gendy = [
	1	5.55 0.2/60 0.2 0.1 0.12 0.15 0.4 0.2 0.2 0.2;
	2	4.33 0.2/60 0.2 0.1 0.12 0.15 0.4 0.2 0.2 0.2;
	3	3.35 0.1/60 0.2 0.1 0.12 0.15 0.4 0.2 0.2 0.2;
];

%% branch data
%	fbus	tbus	r	x	b	rateA	rateB	rateC	ratio	angle	status	angmin	angmax IsTransformer
mpc.branch = [
	1	4	0	    0.0576	0	    250	250	250	0	0	1	-360	360 1;
	4	5	0.017	0.092	0.158	250	250	250	0	0	1	-360	360 0;
	5	6	0.039	0.17	0.358	150	150	150	0	0	1	-360	360 0;
	3	6	0	0.0586	    0       300	300	300	0	0	1	-360	360 1;
	6	7	0.0119	0.1008	0.209	150	150	150	0	0	1	-360	360 0;
	7	8	0.0085	0.072	0.149	250	250	250	0	0	1	-360	360 0;
	8	2	0	    0.0625  0   	250	250	250	0	0	1	-360	360 1;
	8	9	0.032	0.161	0.306	250	250	250	0	0	1	-360	360 0;
	9	4	0.01	0.085	0.176	250	250	250	0	0	1	-360	360 0;
];

%%-----  OPF Data  -----%%
%% generator cost data
%	1	startup	shutdown	n	x1	y1	...	xn	yn
%	2	startup	shutdown	n	c(n-1)	...	c0
% mpc.gencost = [
% 	2	1500	0	3	0.11	5	150;
% 	2	2000	0	3	0.085	1.2	600;
% 	2	3000	0	3	0.1225	1	335;
% ];

%% demand data
%           bus, load, weight
mpc.demand = [  4	5   1;
                4	8   1;
                4   10  1;
                5   7   1;
                5   12  1;
                5   15  1;
	            5	13  1;
	            6	10  1;
                6   10  1;
                6   10  1;
	            7	16  1;
                7   15  1;
	            8   3  1;
                8   13   1;
                8   9   1;
                8   12  1;
	            9	15  1;
                9   6   1;
                9   10  1;
                9   16  1;];

%% ESS data
%         bus   E_max   P_max  eta_cnv eta_sto tau(s)
mpc.ess = [5    50      20     1       1       1];