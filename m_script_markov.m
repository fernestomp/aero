%------------------------------------------------------------------------
% Script con los datos de la matriz de python, que seran convertidos a un
% objeto dtmc de MATLAB. Luego se crea una imagen con la cadena de Markov en
% forma grafica y se carga en el notebook de jupyter
%------------------------------------------------------------------------ 
mat_trans = [77.9131     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan;
21.3278 59.7496     nan     nan 10.2167     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan;
19.6689     nan 62.7385     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan;
16.3294     nan 11.0588 58.5882     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan;
    nan 12.1891     nan     nan 67.5788     nan     nan 11.5672     nan     nan     nan     nan     nan     nan     nan;
    nan     nan     nan     nan     nan 59.3358     nan     nan     nan     nan 10.3321     nan     nan     nan     nan;
    nan     nan 11.2311     nan     nan     nan 70.6263     nan     nan     nan     nan     nan     nan     nan     nan;
    nan     nan     nan     nan 14.3276     nan     nan 68.098      nan     nan     nan     nan     nan     nan     nan;
    nan     nan     nan     nan     nan     nan     nan     nan 80.1765     nan     nan     nan     nan     nan     nan;
    nan     nan     nan     nan     nan     nan     nan 13.6323     nan 62.7914     nan 13.4553     nan     nan     nan;
    nan     nan     nan     nan     nan     nan     nan     nan     nan     nan 70.6498     nan 11.8392     nan     nan;
   nan    nan    nan    nan    nan    nan    nan    nan    nan    nan    nan 72.035    nan    nan    nan;
    nan     nan     nan     nan     nan     nan     nan     nan     nan     nan 12.6392     nan 85.8018     nan     nan;
    nan     nan     nan     nan     nan     nan     nan     nan     nan     nan     nan 14.4462     nan 82.9641     nan;
    nan     nan     nan     nan     nan     nan     nan     nan 10.3612     nan     nan     nan     nan     nan 89.3536;
];
mc = dtmc(mat_trans);
mc.StateNames = ["C1" "C2" "C3" "C4" "C5" "C6" "C7" "C8" "C9" "C10" "C11" "C12" "C13" "C14" "C15"];
p = graphplot(mc,"ColorEdges",true);
layout(p,'circle');
p.MarkerSize =10;
p.NodeFontSize = 14;
p.LineWidth = 1;
p.EdgeAlpha = 1;
colormap("hot");
caxis([0,100]);
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
saveas(gcf,'graph_mc.jpg');
