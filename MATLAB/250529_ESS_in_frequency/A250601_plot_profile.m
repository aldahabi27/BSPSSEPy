%% Parameters
data = [];
time = [];
stepsize = 120; % seconds

%% Preparation of the setpoint series

PL_list = initD' * demand(:,2);
PL_list = PL_list(2:end);

slope_list = zeros(1,T);
for i = 1: T
    % update PL and ramp_slope based on sequence
    if sequence{5,i} ~= 0
        current_gen = sequence{5,i};
        PL_list(i:(i+genprops(current_gen,3)-1)) = PL_list(i:(i+genprops(current_gen,3)-1)) + genprops(current_gen,2);
        ramp_start = i+genprops(current_gen,3); % when the gen starts ramping
        increment = ramprate(current_gen); % ramp rate of the selected gen
        PL_list(ramp_start:(ramp_start + ramptime(current_gen)-1)) = PL_list(ramp_start:(ramp_start + ramptime(current_gen)-1)) ...
            - ((increment:increment:(increment * ramptime(current_gen))) - increment)';

        slope_list(ramp_start:(ramp_start + ramptime(current_gen)-1)) = increment;
    end
end

Pess_list = [];
pickups_list = [];
Pess = diag(eta_cnv)*(sdpPeout) - diag(eta_cnv)^-1*(sdpPein);
pickups = demand(:,2)' * binD;
for k = 1:T
    Pess_list = cat(2,Pess_list, (Pess(k+1) - Pess(k)));
    pickups_list = cat(2,pickups_list, (pickups(k+1) - pickups(k)));
end

bound_vs_pickup = [gradESS(1:T) .* Pess_list + PL_max0(1:T); ((PL_list + slope_list') - [0; (PL_list(1:(end-1)) + slope_list(1:(end-1))')])'];
%% run ode solver
compare = false;
Nstates1 = 1 + 6 * numG;
yinit_1 = zeros(Nstates1,1);

yinits = [];
% yinit_1 = [0 0 0.6 0.6]
for k = 1:T
    disp("FREQ: Running " + k + " of " + T + " timesteps...")
    turn_on = find(binGop(:,k+1) - binGop(:,k));
    if ~isempty(turn_on)
        yinit_1(4+turn_on) = yinit_1(7+turn_on);
    end
    yinits = cat(2, yinits, yinit_1);
    f1 = @(t,y) ieeeG1_SS12(t, y, PL_list(k), slope_list(k)/120, H(k+1), alpha(:,k+1), binGop(:,k+1), 0, tau, Pess(:,k),Pess_list(:,k)); % no damping
    
    tspan = 0.2:0.2:(stepsize);
    M = eye(numG);
    options = odeset('RelTol',1e-3,'AbsTol',1e-6,'MaxStep',0.01);
%     [t1,y1] = ode45(f1,tspan,yinit_1,options);
    [t1,y1] = ode45(f1,tspan,yinit_1,options);
    Pref = PL_list(k)/ sum(alpha(:,k+1));
    % A = [0 0 0 1/(2*H); K/T1 -1/T1 0 0; -(K * T2/ T1/T3) (T2/T1-1)/T3 -1/T3 0; 0 0 1/T4 -1/T4];
    data = cat(1,data,y1);
    time = cat(1, time, t1 + stepsize * (k-1));
    yinit_1 = data(end,:)';
end
%% Analysis
y1 = data;
y1(:,1) =  y1(:,1) * 60; % in Hertz
t1 = time;
% % [M, I] = min(dw1);
% % data = cat(1, data, [t1(I) M])
% % plot(time/60, data(:,1))
% dydt = [];
% for i = 1:length(y1(:,1))
%     dydt = cat(2,dydt,f1(t1(i),y1(i,:)));
% end

offline = zeros(numG, 1);
crank = zeros(numG, 1);
ramp = zeros(numG, 1);
online = zeros(numG, 1);

for i = 1:numG % to plot the bar graph
    offline(i) = max([find(binG(i,:),1)-2, 0]);
    crank(i) = genprops(i, 3);
    ramp(i) = ramptime(i);
    online(i) = T - ramp(i) - crank(i) - offline(i);
end

loads = zeros(numD,1);

for i = 1:T % to plot the load pickup vertical lines
    if sequence{4,i} ~= 0
        loads(sequence{4,i}) = i -1;
    end
end

x = (max(y1(:,1)) - min(y1(:,1)))/20 * -((1:numG) - (numG+1)/2) + max(y1(:,1)) + 0.01;
y = [offline, crank, ramp, online];

f1 = figure;
yyaxis right

bargraph = barh(x,y(:,1:4), "stacked");

myColors = [0.8 0.8 0.8; 1 0.5 0.5; 1 1 0.5; 0.5 1 0.5];
for i = 1:4
    bargraph(i).FaceColor = 'flat';
    bargraph(i).CData = myColors(i,:);
    bargraph(i).BarWidth = 1;
end
text(59.5, 0.9,"GEN 1",'HorizontalAlignment','right','Color','black');
text(59.5, 0.8,"GEN 2",'HorizontalAlignment','right','Color','black');
text(59.5, 0.7,"GEN 3",'HorizontalAlignment','right','Color','black');

yticks([])
yticklabels("Gen " + string(numG:-1:1))
ylim([min(y1(:,1))+0.5, max(x)+0.1])
set(gca,'YColor','black')
xline(loads(1:numD),"-","LineStyle","--","LabelVerticalAlignment","top",'Color',0.7*[1 1 1]);

% xline(loads,"-","D" + string(1:numD) + " " + string(100 * demand(:,2))' + "MW","LineStyle","--","LabelVerticalAlignment","bottom");
hold on
yyaxis left
set(gca,'YColor','black','FontSize',14)
plot(time/stepsize, y1(:,1))
ylim([min(y1(:,1)) - 0.8, max(x) + 0.8])
yline(-60*freq_limit,"-","$f_{\rm lim}$","LineStyle","--","Color","red",'Interpreter','latex','FontSize',16)
grid minor
xlabel("$t$ [$k$]",'FontSize',18)
ylabel("$\Delta f$ [Hz]",'FontSize',18)
lgd = legend(bargraph,"Offline","Crank","Ramp-up","In service",'location','best','numcolumns',2,'iconcolumnwidth',16,'fontsize',16);
lgd.Title.String = "Gen Phases";
[loadsorted, I] = sort(loads)
text(loadsorted(1:3:numD), -1.2*ones(length(1:3:numD),1),string(I(1:3:numD)),'interpreter','latex','fontsize',14)
text(loadsorted(2:3:numD), -1.4*ones(length(2:3:numD),1),string(I(2:3:numD)),'interpreter','latex','fontsize',14)
text(loadsorted(3:3:numD), -1.6*ones(length(3:3:numD),1),string(I(3:3:numD)),'interpreter','latex','fontsize',14)

% ,s'LabelColor','black',
