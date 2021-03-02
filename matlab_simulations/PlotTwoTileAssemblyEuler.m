% Euler's Method
% For Two Active Tile ODE

clear all;
close all;

Parameters
% p.n = 2.5; % stoichiometric constant
% p.k_nuc = 2.0*1e5; %*(1e9)^(1 - p.n);
% p.k_elong = 3.4*1e6; %*1e-9; % rate constants in nM
%
SIM_TIME = 24; % simulation time in an hour
HOUR = 3600; % secs in hour

TIME_STEP = 0.1;

initTileConc = [50, 100, 250]*1e-9;

tspan = [0:TIME_STEP:SIM_TIME*HOUR];

tSln = zeros(length(tspan), length(initTileConc));

for z=1:length(initTileConc)
    initTileA = initTileConc(z);
    initTileB = initTileConc(z);
    initNuc = 0;
    
    INIT_TILES = initTileA + initTileB;
    
    tileA_0 = initTileA;
    tileB_0 = initTileB;
    nuc_0 = initNuc;
    
    % euler loop starts here
    for c=2:length(tspan)
        % calculate the y_1's of the tangent line
        tileA_1 = TIME_STEP*(-(par.n/2)*(par.k_nuc)*(tileA_0^(par.n/2))*(tileB_0^(par.n/2)) - (1/2)*par.k_elong*nuc_0*tileA_0) + tileA_0;
        tileB_1 = TIME_STEP*(-(par.n/2)*(par.k_nuc)*(tileA_0^(par.n/2))*(tileB_0^(par.n/2)) - (1/2)*par.k_elong*nuc_0*tileB_0) + tileB_0;
        nuc_1 = TIME_STEP*((par.k_nuc)*(tileA_0^(par.n/2))*(tileB_0^(par.n/2))) + nuc_0;
        % compute tiles assembled
        tSln(c, z) = (INIT_TILES - tileA_1 - tileB_1) / (INIT_TILES);
        tSl(c, z) = (INIT_TILES - tileA_1 - tileB_1);
        
        NanotubeConcentration(c,z)= nuc_1; %  NANOTUBE CONCENTRATION
        FreeTileA(c,z)=tileA_1;
        FreeTileB(c,z)=tileB_1;
        % update y_0's
        tileA_0 = tileA_1;
        tileB_0 = tileB_1;
        nuc_0 = nuc_1;
    end
    
    
end

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%% FIRST PLOT -- CONCENTRATION OF ASSEMBLED TILES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

colorList(1, :) = rgb('Lavender');
colorList(2, :) = rgb('Amethyst');
colorList(3, :) = rgb('Indigo');


for i=1:length(initTileConc)
    plot(tspan/60, tSln(:, i), 'Color', colorList(i, :), 'LineWidth', 3);
    hold on;
end

xlabel('Time (min)');
ylabel('Fraction of Assembled Tiles');
legend('Each tile [50 nM]', 'Each tile [100 nM]', 'Each tile [250 nM]');
legend boxoff

ylim([0, 1]);

xlim([0, 60*6]);

Width=10;
Height=8;
%%%% PDF %%%%%%%%%%%%%
set(gcf, 'PaperUnits', 'centimeters'); % SETS THE PAPER UNITS
set(gcf, 'PaperPosition', [0 0 Width Height]); % SETS THE FIGURE SIZE
set(gcf, 'PaperSize', [Width Height]); % CUTS THE FIGURE
print(gcf,'-dpdf', 'TwoTilePlot.pdf') % PRINTS TO A FILE.

%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% SECOND FIGURE - ESTIMATED NUMBER OF NANTUBES IN A
%%%%%%%%%%%%%%%%%% DROPLET OF 3µm RADIUS.
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

colorListN(1, :) = rgb('YellowGreen');
colorListN(2, :) = rgb('MediumSeaGreen');
colorListN(3, :) = rgb('DarkGreen');

radius=3e-6; % droplet radius
Vol=(4/3)*pi*radius^3; % droplet volume
DropletVolume=Vol*1e3; % volume converted to liters
NA=6e23; % Avogadro's number

figure
for i=1:length(initTileConc)
    plot(tspan/60, NanotubeConcentration(:, i)*DropletVolume*NA, 'Color', colorListN(i, :), 'LineWidth', 3);
    hold on;
end

xlabel('Time (min)');
ylabel('Number of nanotubes');
legend('Each tile [50 nM]', 'Each tile [100 nM]', 'Each tile [250 nM]');
legend boxoff

xlim([0, 60*6]);
title('Estimate for a droplet with 3\mu m radius ')



Width=10;
Height=8;
%%%% PDF %%%%%%%%%%%%%
set(gcf, 'PaperUnits', 'centimeters'); % SETS THE PAPER UNITS
set(gcf, 'PaperPosition', [0 0 Width Height]); % SETS THE FIGURE SIZE
set(gcf, 'PaperSize', [Width Height]); % CUTS THE FIGURE
print(gcf,'-dpdf', 'TwoTileNanotubePlot.pdf') % PRINTS TO A FILE.



%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%
%%%%%%%%%%%%%%%%%% THIRD FIGURE - FREE TILES
%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%%

colorListF(1, :) = rgb('GoldenRod');
colorListF(2, :) = rgb('Orange');
colorListF(3, :) = rgb('Red');


figure
for i=1:length(initTileConc)
    plot(tspan/60, FreeTileA(:, i)*1e9, 'Color', colorListF(i, :), 'LineWidth', 3);
    hold on;
end

xlabel('Time (min)');
ylabel('Free tile A concentration (nM)');
legend('Each tile [50 nM]', 'Each tile [100 nM]', 'Each tile [250 nM]');
legend boxoff

xlim([0, 60*6]);



Width=10;
Height=8;
%%%% PDF %%%%%%%%%%%%%
set(gcf, 'PaperUnits', 'centimeters'); % SETS THE PAPER UNITS
set(gcf, 'PaperPosition', [0 0 Width Height]); % SETS THE FIGURE SIZE
set(gcf, 'PaperSize', [Width Height]); % CUTS THE FIGURE
print(gcf,'-dpdf', 'TwoTileFreeTilePlot.pdf') % PRINTS TO A FILE.


% figure
% for i=1:length(initTileConc)
%     plot(tspan/60, (FreeTileA(:, i)./initTileConc(i)), 'Color', colorListF(i, :), 'LineWidth', 3);
%     hold on;
% end
% 
% title('Ratio free/assembled')