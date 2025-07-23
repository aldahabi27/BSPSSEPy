function dydt = ieeeG1_SS12(t, y, PL, ramp_slope, H, alpha, binGop, D, tau, Pess_0, dPess)
% This model only has one lag filter block for the turbine action G_T(s)
% This model neglects the deadzone block for dw
% With multiple generators
% Fixed units of alpha and changed Pref accordingly
% Has damping as an input
% Has ESS setpoint changes as an input

%% Parameters
% y contains w (1-dimensional), and x, atilde, Pm (each G-dimensional)
numG = length(alpha);
if size(y,1) == 1
    y = y';
end
% Pref =  (PL/sum(alpha)) * [1; 1; 1];
% Pref =  [(PL-0.3)/1.6;0.3+(PL-0.3)/1.6;0];
% Pref = ones(numG,1) * PL / sum(alpha);
PL_net = PL;

if ramp_slope > 0
    PL_net = PL  - ramp_slope * t;
end

K = 20;
T1 = 4* ones(numG,1);
T2 = 8* ones(numG,1);
T3 = 0.2 * ones(numG,1);
T4 = 0.2 * ones(numG,1);
T5 = 0.12 * ones(numG,1);
T6 = 0.12 * ones(numG,1);
T7 = 0.15 * ones(numG,1);
K1 = 0.4; K3 = 0.2;
K5 = 0.2; K7 = 0.2;

% Uo = 0.3 * ones(numG,1);
Uo = [0.2, 0.2, 0.1]/60;
Uc = -[0.2, 0.2, 0.1]/60;
Pmax = [1; 1; 1];
Pmin = [0; 0.2; 0.2];

% D = 20;

% Pref corrections

Pref = zeros(numG,1);
PL_remaining = PL - 60*ramp_slope - (Pess_0 + dPess); % NOTE: 60 is half of a timestep length.
for i = 1:numG
    if Pref(i) < Pmin(i) && binGop(i) == 1  % if Pref is less than Pmin for any online unit
        PL_remaining = PL_remaining - alpha(i)*Pmin(i); % remove Pmin amount of load from the pool
        Pref(i) = Pmin(i); % and assign it to that unit
    end
end
Pref = Pref + ones(numG,1) * (PL_remaining) / sum(alpha); % split up the remaining pool equally among the units
Pref = Pref .* (alpha > 0);
%% Equations
    dw = y(1);
    x = y(2:(numG + 1));
    atilde = y((numG + 2):(2*numG + 1));
    PT1 = y((2*numG + 2):(3*numG + 1));
    PT2 = y((3*numG + 2):(4*numG + 1));
    PT3 = y((4*numG + 2):(5*numG + 1));
    PT4 = y((5*numG + 2):(6*numG + 1));
    Pm = K1 * PT1 + K3 * PT2 + K5 * PT3 + K7 * PT4;

    dydt = [(1/(2*H)) * (alpha' * Pm - PL_net - D * dw + (Pess_0 + dPess*(1-exp(-t./tau))));
            binGop .* (1./T1) .* (-x + K * ones(numG,1) * dw);
            binGop .* saturation((1./T3).*((1 - T2./T1) .* -x - (K .* T2./T1) * dw - saturation(atilde, Pmax, Pmin) + Pref), Uo, Uc);
%             binGop .* Uo .* (1 - exp(-(1./(T3.*Uo)).*((1 - T2./T1) .* -x - (K .* T2./T1) * dw - saturation(atilde, Pmax, Pmin) + Pref)));
            (1./T4) .* (-PT1 + saturation(atilde, Pmax, Pmin));
            (1./T5) .* (-PT2 + PT1);
            (1./T6) .* (-PT3 + PT2);
            (1./T7) .* (-PT4 + PT3)
        ];

end