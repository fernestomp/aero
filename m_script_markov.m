%------------------------------------------------------------------------
% Script con los datos de la matriz de python, que seran convertidos a un
% objeto dtmc de MATLAB. Luego se crea una imagen con la cadena de Markov en
% forma grafica y se carga en el notebook de jupyter
%------------------------------------------------------------------------ 
mat_trans = [9.51823452e-01 3.16065083e-02 1.36899196e-02 2.58088648e-03 2.99233215e-04;
0.14542636 0.71550388 0.07224806 0.04790698 0.01891473;
0.06305267 0.09034987 0.69800077 0.13110342 0.01749327;
0.00455975 0.06367925 0.10345912 0.75990566 0.06839623;
4.69924812e-04 2.58458647e-02 1.90319549e-02 1.09022556e-01 8.45629699e-01;
];
mc = dtmc(mat_trans);
mc.StateNames = ["C1" "C8" "C10" "C12" "C14"];
p = graphplot(mc,"ColorEdges",true);
layout(p,'auto');
p.MarkerSize =10;
p.NodeFontSize = 14;
p.LineWidth = 1;
p.EdgeAlpha = 1;
colormap("hot");
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
saveas(gcf,'graph_mc_joined.jpg');
