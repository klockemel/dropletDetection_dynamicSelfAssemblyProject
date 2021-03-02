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

Template=[7.5 25 50 100];

Pink=rgb('HotPink');
Purple=rgb('Maroon');
Green=rgb('DarkOliveGreen');
LGreen=rgb('YellowGreen');
LBlue=rgb('LightBlue');
DBlue=rgb('DarkBlue');
LRed=rgb('LightCoral');
DRed=rgb('FireBrick');
Black=rgb('Black');
Gray=rgb('LightGray');

 N=4;

ColorPlot(1,:)=rgb('LightBlue');
ColorPlot(2,:)=rgb('CadetBlue');
ColorPlot(3,:)=rgb('RoyalBlue');
ColorPlot(4,:)=rgb('Navy');


for i=1:4
tspan = [0:1:6*hours];
par.TrTot = Template(i)*1e-9;
par.TileTot = 500*1e-9;
par.RNAP_TOT = 54*1e-9;
par.RHtot=0;
par.realTileTot=par.TileTot;

x0_ideal = [par.TrTot, 0, par.TileTot, 0, 0, 0, 0, 0, par.RHtot, 0, par.RNAP_TOT];
[tv, Yv] = ode23(@NoInhControlODE, tspan,  x0_ideal, options, par);
compNT(:) = Yv(:, 6);
compActT(:) = Yv(:, 7);
compAT (:) = Yv(:, 8);
RnaT (:) = Yv(:, 2);
tileSln(:) = (par.TileTot - Yv(:, 3) - Yv(:, 4)) / (par.TileTot);

 
plot(tspan/60, tileSln, 'Color', ColorPlot(i,:), 'LineWidth', 3);
hold on;
end
legend('7.5 nM gene', '25 nM gene', '50 nM gene', '100 nM gene','Location','East')
legend boxoff
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
print(gcf,'-dpdf', 'TemplatePlot.pdf') % PRINTS TO A FILE.


