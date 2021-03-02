
function dcdt = NoInhControlODE(t,c,p)

t_rna = c(1);  rnaT = c(2);
offTile = c(3); activeTile = c(4); nt = c(5); rnaseH_nt = c(6); 
rnaseH_activeTile = c(7); rnaseH_assembledTiles = c(8);
rnaseH = c(9); 
rnap_t_rna = c(10); 
rnap = c(11); 



assembledTiles = p.realTileTot - offTile - activeTile - rnaseH_activeTile - nt - rnaseH_nt - rnaseH_assembledTiles;

dt_rna = p.k_cat_on*rnap_t_rna + p.k_rnap_r*rnap_t_rna - p.k_rnap_f*rnap*t_rna;
drnaT = p.k_cat_on*rnap_t_rna - p.k_ai_1*rnaT*offTile; %+ (K_CAT_OFF_12/K_M_OFF_12)*rnap*t_rna

doffTile = -p.k_ai_1*rnaT*offTile + p.K_CAT_H_2*rnaseH_nt + p.K_CAT_H_2*rnaseH_activeTile + p.K_CAT_H_2*rnaseH_assembledTiles;
dactiveTile =  p.k_ai_1*rnaT*offTile + p.k_h_r*rnaseH_activeTile  - p.n*p.k_nuc*(activeTile^(p.n)) - p.k_h_f*rnaseH*activeTile - p.k_elong*nt*activeTile ;

dnt = p.n*p.k_nuc*(activeTile^(p.n)) - p.k_h_f*nt*rnaseH + p.k_h_r*rnaseH_nt;
drnaseH_nt = p.k_h_f*nt*rnaseH - p.k_h_r*rnaseH_nt - p.K_CAT_H_2*rnaseH_nt;
drnaseH_activeTile = p.k_h_f*activeTile*rnaseH - p.k_h_r*rnaseH_activeTile - p.K_CAT_H_2*rnaseH_activeTile;

drnaseH_assembledTiles = p.k_h_f*assembledTiles*rnaseH - p.k_h_r*rnaseH_assembledTiles - p.K_CAT_H_1*rnaseH_assembledTiles; 

drnaseH = p.K_CAT_H_2*rnaseH_activeTile + p.K_CAT_H_2*rnaseH_nt ...
         + p.k_h_r*rnaseH_nt + p.k_h_r*rnaseH_activeTile ...
         - p.k_h_f*nt*rnaseH - p.k_h_f*activeTile*rnaseH ...
         - p.k_h_f*assembledTiles*rnaseH + p.k_h_r*rnaseH_assembledTiles + p.K_CAT_H_1*rnaseH_assembledTiles;  

drnap_t_rna = p.k_rnap_f*rnap*t_rna - p.k_rnap_r*rnap_t_rna - p.k_cat_on*rnap_t_rna; 
drnap = p.k_cat_on*rnap_t_rna - p.k_rnap_f*rnap*t_rna + p.k_rnap_r*rnap_t_rna - .5*0.00038*rnap;
dcdt = [dt_rna drnaT doffTile dactiveTile dnt drnaseH_nt drnaseH_activeTile drnaseH_assembledTiles drnaseH drnap_t_rna drnap]';

end
