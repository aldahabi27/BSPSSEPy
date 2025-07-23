function [GEN, LOAD, BRANCH, ESS] = F250204_element_names(mpc)

    letters = string(('A':'Z')'); % the alphabet

    numG = length(mpc.gen(:,1));
    numL = length(mpc.demand(:,2));
    numB = length(mpc.branch(:,1));
    numE = length(mpc.ess(:,1));

    % differentiate between transformers and lines
    IsLine = find(mpc.branch(:,end)==0);
    IsTransformer = find(mpc.branch(:,end)==1);
    % TWTF and BRN bus numbers are ordered
    Tbuses = sort(mpc.branch(IsTransformer,1:2),2);
    Lbuses = sort(mpc.branch(IsLine,1:2),2);
    
    Gnames = [repmat("GEN",[length(mpc.gen(:,1)),1]), "GEN" + string(mpc.gen(:,1))]; % Generator names
    Lnames = [repmat("LOAD",[length(mpc.demand(:,1)),1]), "LOAD" + string(mpc.demand(:,1))]; % Load names
    Enames = [repmat("BESS",[length(mpc.ess(:,1)),1]), "BESS" + string(mpc.ess(:,1))]; % ESS names
    
    TWTF = "TWTF" + string(Tbuses(:,1)) + "_" + string(Tbuses(:,2)); % Transformer names
    BRN = "BRN" + string(Lbuses(:,1)) + "_" + string(Lbuses(:,2)); % Line names
    
    Bnames = string(zeros(length(mpc.branch(:,1)),2));
    Bnames(IsTransformer,:) = [repmat("TRN",[length(IsTransformer), 1]), TWTF];
    Bnames(IsLine,:) = [repmat("BRN",[length(IsLine), 1]), BRN];
    

    % correcting names if multiple of an element is on the same bus
    % if changed from previous bus AND same as following bus
        % assign letters to the names from ABC
    % otherwise do not assign letters
    
    LOAD = Lnames;
    for i = find((Lnames(:,2) ~= ["0"; Lnames(1:end-1,2)])' .* ([Lnames(2:end,2); "0"] == Lnames(:,2))')
        LOAD(i:end,2) = Lnames(i:end,2) + letters(1:(numL - i + 1));
    end

    GEN = Gnames;
    for i = find((Gnames(:,2) ~= ["0"; Gnames(1:end-1,2)])' .* ([Gnames(2:end,2); "0"] == Gnames(:,2))')
        GEN(i:end,2) = Gnames(i:end,2) + letters(1:(numG - i + 1));
    end

    BRANCH = Bnames;
    for i = find((Bnames(:,2) ~= ["0"; Bnames(1:end-1,2)])' .* ([Bnames(2:end,2); "0"] == Bnames(:,2))')
        BRANCH(i:end,2) = Bnames(i:end,2) + letters(1:(numB - i + 1));
    end

    ESS = Enames;
    for i = find((Enames(:,2) ~= ["0"; Enames(1:end-1,2)])' .* ([Enames(2:end,2); "0"] == Enames(:,2))')
        Enames(i:end,2) = Enames(i:end,2) + letters(1:(numB - i + 1));
    end
end
%{
function [GEN, LOAD, BRANCH, ESS] = F250204_element_names(mpc)

    letters = string(('A':'Z')'); % the alphabet

    numG = length(mpc.gen(:,1));
    numL = length(mpc.demand(:,2));
    numB = length(mpc.branch(:,1));

    % differentiate between transformers and lines
    IsLine = find(mpc.branch(:,end)==0);
    IsTransformer = find(mpc.branch(:,end)==1);
    % TWTF and BRN bus numbers are ordered
    Tbuses = sort(mpc.branch(IsTransformer,1:2),2);
    Lbuses = sort(mpc.branch(IsLine,1:2),2);
    
    Gnames = [repmat("GEN",[length(mpc.gen(:,1)),1]), "GEN" + string(mpc.gen(:,1))]; % Generator names
    Lnames = [repmat("LOAD",[length(mpc.demand(:,1)),1]), "LOAD" + string(mpc.demand(:,1))]; % Load names
    
    TWTF = "TWTF" + string(Tbuses(:,1)) + "_" + string(Tbuses(:,2)); % Transformer names
    BRN = "BRN" + string(Lbuses(:,1)) + "_" + string(Lbuses(:,2)); % Line names
    
    Bnames = string(zeros(length(mpc.branch(:,1)),2));
    Bnames(IsTransformer,:) = [repmat("TRN",[length(IsTransformer), 1]), TWTF];
    Bnames(IsLine,:) = [repmat("BRN",[length(IsLine), 1]), BRN];

    % correcting names if multiple of an element is on the same bus
    % if changed from previous bus AND same as following bus
        % assign letters to the names from ABC
    % otherwise do not assign letters
    
    LOAD = Lnames;
    for i = find((Lnames(:,2) ~= ["0"; Lnames(1:end-1,2)])' .* ([Lnames(2:end,2); "0"] == Lnames(:,2))')
        LOAD(i:end,2) = Lnames(i:end,2) + letters(1:(numL - i + 1));
    end

    GEN = Gnames;
    for i = find((Gnames(:,2) ~= ["0"; Gnames(1:end-1,2)])' .* ([Gnames(2:end,2); "0"] == Gnames(:,2))')
        GEN(i:end,2) = Gnames(i:end,2) + letters(1:(numG - i + 1));
    end

    BRANCH = Bnames;
    for i = find((Bnames(:,2) ~= ["0"; Bnames(1:end-1,2)])' .* ([Bnames(2:end,2); "0"] == Bnames(:,2))')
        BRANCH(i:end,2) = Bnames(i:end,2) + letters(1:(numB - i + 1));
    end

end

%}