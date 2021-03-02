clear all;
close all;

Parameters
nM=1e9;
hours=3600;
TimePerturbation=4;
Ttot=7;
options = odeset('AbsTol', 1e-15);
tspan = [0:1:6*hours];
N_AVO = 6.022 * 1e23;

%Rh=2.5*[0 .5 1 2];
Rh=[0 1.6 3.2 4.6 6.4];

Pink=rgb('HotPink');
Purple=rgb('Maroon');
Green=rgb('DarkOliveGreen');
LGreen=rgb('YellowGreen');
LBlue=rgb('LightBlue');
DBlue=rgb('DarkBlue');
LRed=rgb('MediumVioletRed');
DRed=rgb('LightCoral');
Black=rgb('Black');
Gray=rgb('LightGray');

N=4;


ColorPlotS=[flipud(linspace(LBlue(1),DBlue(1),N)'),...
    flipud(linspace(LBlue(2),DBlue(3),N)'),...
    flipud(linspace(LBlue(3),DBlue(3),N)')];

ColorPlotI=[flipud(linspace(LRed(1),DRed(1),N)'),...
    flipud(linspace(LRed(2),DRed(3),N)'),...
    flipud(linspace(LRed(3),DRed(3),N)')];

ColorPlotR=[flipud(linspace(Gray(1),Black(1),N)'),...
    flipud(linspace(Gray(2),Black(3),N)'),...
    flipud(linspace(Gray(3),Black(3),N)')];

ColorPlotL=[flipud(linspace(Pink(1),Purple(1),N)'),...
    flipud(linspace(Pink(2),Purple(3),N)'),...
    flipud(linspace(Pink(3),Purple(3),N)')];


for i=1:5
    tspan = [0:1:6*hours];
    par.TrTot = 100*1e-9;
    par.TileTot = 500*1e-9;
    par.RNAP_TOT = 54*1e-9;
    par.RHtot= Rh(i)*1e-9;
    DROPLET_RADIUS = 8e-6;
    par.realTileTot=par.TileTot;
    
    x0_ideal = [par.TrTot, 0, par.TileTot, 0, 0, 0, 0, 0, par.RHtot, 0, par.RNAP_TOT];
    [tv, Yv] = ode45(@NoInhControlODE, tspan,  x0_ideal, options, par);
    compNT(:) = Yv(:, 6);
    compActT(:) = Yv(:, 7);
    compAT (:) = Yv(:, 8);
    RnaT (:) = Yv(:, 2);
    tileSln(:) = (par.TileTot - Yv(:, 3) - Yv(:, 4)) / (par.TileTot);
    
    if i==1
        plot(tspan/60, tileSln,'.', 'Color', rgb('DarkGray'), 'LineWidth', 3,'MarkerFaceColor', rgb('DarkGray'));
        hold on;
        text(100,1-0.1*i,['No RNase H'],'Color',rgb('DarkGray'),'FontSize',10);

    else
        plot(tspan/60, tileSln,'.', 'Color', ColorPlotI(i-1,:), 'LineWidth', 3,'MarkerFaceColor', ColorPlotI(i-1,:));
        hold on;
        
       text(100,1-0.1*i,['RNase H ' num2str(Rh(i)) ' nM'],'Color',ColorPlotI(i-1,:),'FontSize',10);

    end
end

 
% legend('No RNase H', '1.6 nM RNase H', '3.2 nM RNase H', '4.8 nM RNase H', '6.4 nM RNase H')
% legend boxoff

xlim([0 60*6]) ;
ylim([0 1]);
xlabel('Time (min)');
ylabel('Fraction of Assembled Tiles');

Width=8;
Height=6;
%%%% PDF %%%%%%%%%%%%%
set(gcf, 'PaperUnits', 'centimeters'); % SETS THE PAPER UNITS
set(gcf, 'PaperPosition', [0 0 Width Height]); % SETS THE FIGURE SIZE
set(gcf, 'PaperSize', [Width Height]); % CUTS THE FIGURE
print(gcf,'-dpdf', 'RNaseHPlotFinal.pdf') % PRINTS TO A FILE.


