%------------------------------------------------------------------------
% Script con los datos de la matriz de python, que seran convertidos a un
% objeto dtmc de MATLAB. Luego se crea una imagen con la cadena de Markov en
% forma grafica y se carga en el notebook
%------------------------------------------------------------------------ 
mat_trans = [9.52920630e-01 3.11385256e-02 1.09244946e-02 4.57045184e-03 4.45897741e-04;
0.14081914 0.72787237 0.0139592  0.11351434 0.00383494;
0.09873249 0.03468979 0.74916611 0.08038692 0.03702468;
0.00867736 0.10820405 0.03273731 0.78648435 0.06389692;
4.44938821e-04 1.33481646e-03 2.33592881e-02 1.15461624e-01 8.59399333e-01;
];
mat_trans(isnan(mat_trans))=0;
mc = dtmc(mat_trans);
mc.StateNames = ["E1" "E2" "E3" "E4" "E5"];
p = graphplot(mc,"ColorEdges",true);
colorbar off;
layout(p,'auto');
p.MarkerSize =30;
p.NodeFontSize = 15;
p.LineWidth = 2;
p.NodeLabelColor ="blue";
p.EdgeFontSize = 15;
p.ArrowSize = 20;
p.ArrowPosition=.93;
p.EdgeAlpha = 1;
colormap("copper");
if isempty(find(isnan(mat_trans), 1))
   p.EdgeLabelMode= 'auto';
else
   p.EdgeLabelMode= 'manual';
   idx =find(~isnan(mat_trans));
   vals = mat_trans(idx);
   labeledge(p,idx,vals);
end
set(gcf, "PaperUnits", "inches");
set(gcf, "PaperPosition", [0 0 20 10]);
saveas(gcf,'graph_mc_ca.jpg');
