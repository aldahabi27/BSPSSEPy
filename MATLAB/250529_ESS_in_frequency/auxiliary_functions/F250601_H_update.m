function [H, alpha, PL_max, gradESS] = F250601_H_update(H, alpha, it, binG, mpc, T, t, wlim, tau)

% This version uses alphas in XYZ calculations with standard H and alpha
% values
%  This version considers ESS contributions but not damping
PL_max = zeros(1,T+t);
gradESS = zeros(length(mpc.ess(:,1)), T+t);
gendy = mpc.gendy; %dynamic info
genMax = mpc.gen(:,2); % capacity
genMin = mpc.gen(:,3); % min output

ramptime = round(genMin./(genMax .* mpc.gen(:,6) / 100));

genTime = mpc.gen(:,5) + ramptime; % total time from cranking to full operation
genCrank = mpc.gen(:,5); % cranking time only

numG = length(gendy(:,1));
genH = gendy(:,2);

%IEEEG1 paramters
U0 = gendy(:,3);
T4 = gendy(:,4);
T5 = gendy(:,5);
T6 = gendy(:,6);
T7 = gendy(:,7);
K1 = gendy(:,8);
K3 = gendy(:,9);
K5 = gendy(:,10);
K7 = gendy(:,11);

    % If it's the first iteration, initialize using only the BSU
    if it == 1
        H = genH(1) * genMax(1) * ones(1, T + t) /100;
        alpha = [genMax(1)/100; zeros(numG - 1, 1)] * ones(1, T + t);
       
    else
        genChange = binG(:,end) - binG(:,end-1); % check if status changed
        if ~isempty(find(genChange, 1)) % if a generator was picked up in the most recent step
            genNew = find(genChange); % find which unit started
%             genActive = find(binG(:,end)); % which gens are active at the current time step
            
            alpha(genNew, (length(binG)+genTime(genNew)):(T+t)) = genMax(genNew)/ 100;
            H((length(binG)+genCrank(genNew)):(T+t)) = H((length(binG)+genCrank(genNew)):(T+t)) + genMax(genNew) * genH(genNew) / 100;
            
        end
    end

    % finding PL_max

    final_coeff = zeros(numG, 3);
    final_coeff(:,1) = K1 + K3 + K5 + K7; % coefficients for the 1 term
    final_coeff(:,2) = - (- T4.*(K1 + K3 + K5 + K7) - T6.*(K5 + K7) - T5.*(K3 + K5 + K7) - K7.*T7); % coeff is defined with subtraction, coefficients for the s term
    final_coeff(:,3) = (T6.^2.*(K5 + K7) + T5.^2.*(K3 + K5 + K7) + K7.*T7.^2 + T4.^2.*(K1 + K3 + K5 + K7)...
                     + T4.*(T6.*(K5 + K7) + T5.*(K3 + K5 + K7) + K7.*T7) + T5.*(T6.*(K5 + K7) + K7.*T7) + K7.*T6.*T7); % coefficients for the s^2 term
    
    for i = 1:(T+t)
        Xbar = alpha(:,i)' * diag(U0) * final_coeff(:,1);
        Ybar = alpha(:,i)' * diag(U0) * final_coeff(:,2);
        Zbar = alpha(:,i)' * diag(U0) * final_coeff(:,3);
%         w(i) = -((PL(i) + Y)^2 - 2 * X * Z)/(4*H(i+1)*X);
        PL_max(i) = sqrt(2*Xbar*Zbar + 4 * H(i) * Xbar * wlim) - Ybar;

        gradESS(:,i) = 1 - 2*Xbar.*tau/(2*sqrt(2*Xbar*Zbar + 4 * H(i) * Xbar * wlim));

    end

end