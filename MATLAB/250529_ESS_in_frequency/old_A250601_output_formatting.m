mpc = case9f_newmodel;
[GEN, LOAD, BRANCH] = F250204_element_names(mpc); % Obtain names of the elements

%% Analysis
output_plan = ["Device Type", "Identification Type", "Identification Value", "Action Type", "Action Time", "Action Status", "Values"];

dev_types = [BRANCH(:,1);LOAD(:,1);GEN(2:end,1)];
id_values = [BRANCH(:,2);LOAD(:,2);GEN(2:end,2)]; % names of the elements in order


% activateX matrices has entry 1 in row i at the timestep the ith element turns on.
activateL = [binL(:,2:end) ones(numL, 1)] - binL;
activateD = [binD(:,2:end) ones(numD, 1)] - binD;
activateG = [binG(2:end,2:end) ones(numG -1, 1)] - binG(2:end,:);

% updateG matrix has nonzero value when the output changes at the timestep
updateG = sdpPG - [zeros(numG, 1), sdpPG(:,1:end-1)];
updateG = abs(updateG) > 1e-5;

[rowG,colG] = find(updateG);

[row,col] = find([activateL; activateD; activateG]); % find when each element turns on

[col, colI] = sort(col); % reorganizing in order of turning on
row = row(colI);
id_values = id_values(row);
dev_types = dev_types(row);

col = [col; -1];
colI = [colI; -1];
count = 1;
countG = 1;
for i = 1:T
    while i == col(count)
        output_plan = cat(1, output_plan, [dev_types(count), "NAME", id_values(count), "ON", col(count), 0, "{}"]);
        count = min([count+1, length(col)]);
    end
    while i == colG(countG)
        if sdpPG(rowG(countG),colG(countG)) > 0 % if output is negative, NBSU is cranking so we skip that
            output_plan = cat(1, output_plan, ["GEN", "NAME", GEN(rowG(countG),2), "UPDATE", colG(countG), 0, "{'P': " + string(baseMVA*sdpPG(rowG(countG),colG(countG))) + "}"]);
        end
        countG = min([countG+1, length(colG)]);
    end
end

writematrix(output_plan,"plan" + string(today("datetime")) + ".csv")


