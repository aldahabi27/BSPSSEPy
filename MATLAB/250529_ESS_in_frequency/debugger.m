% Select a time range to inspect
t_look = [27 31];
if ~isempty(find(t_look > T, 1)) || ~isempty(find(t_look < 1, 1))
    disp("Invalid range t_look")
    return
end

% making variables to display
crank_list = genprops(:,2)' * binGcrank(:,2:end);

% displaying variable information

range = "(" + string(t_look(1)) + ":" + string(t_look(2)) + ")"
disp("PL_list" + range + " = " + mat2str(PL_list(t_look(1):t_look(2))'))
disp("pickups_list" + range + " = " + mat2str(pickups_list(t_look(1):t_look(2))))
disp("crank_list" + range + " = " + mat2str(crank_list(t_look(1):t_look(2))))
disp("slope_list" + range + " = " + mat2str(slope_list(t_look(1):t_look(2))))
disp("Pess_list" + range + " = " + mat2str(Pess_list(t_look(1):t_look(2))))
disp("bound" + range + " = " + mat2str(bound_vs_pickup(1,t_look(1):t_look(2))))
disp("pickup" + range + " = " + mat2str(bound_vs_pickup(2,t_look(1):t_look(2))))



%% run ode solver with arbitrary starting step
data = [];
time = [];

t_start = 30;
Pref = [0.7693;0;0];
for k = t_start

    disp("FREQ: Running " + k + " of " + T + " timesteps...")
    turn_on = find(binGop(:,k+1) - binGop(:,k));

    % PL_remaining = PL_list(k) - 60*slope_list(k)/120 - (Pess(:,k) + Pess_list(:,k)) - alpha(:,k+1)'*(Pref + genMin)

    f1 = @(t,y) ieeeG1_SS12(t, y, PL_list(k), slope_list(k)/120, H(k+1), alpha(:,k+1), binGop(:,k+1), 0, tau, Pess(:,k),Pess_list(:,k)); % no damping
    
    tspan = 0.2:0.2:(stepsize);
    M = eye(numG);
    options = odeset('RelTol',1e-3,'AbsTol',1e-6,'MaxStep',0.01);
%     [t1,y1] = ode45(f1,tspan,yinit_1,options);
    [t1,y1] = ode45(f1,tspan,yinits(:,k),options);
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

figure
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
hold off