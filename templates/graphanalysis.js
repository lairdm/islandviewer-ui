var graph = {{ json_str|safe }};
var g = new dagreD3.Digraph();

var name_substitutions = {Virulence: 'Annotating Genes',
						  Summary: 'Validating Pipeline'};

var nodes = graph['nodes'];
for(node in nodes) {
	var nodelabel = nodes[node]['name'];
	if('undefined' !== typeof(name_substitutions[nodelabel])) {
		nodelabel = name_substitutions[nodelabel];
	}
	g.addNode(nodes[node]['name'], {label: nodelabel, nodeclass: nodes[node]['status']});
}
var edges = graph['edges'];
for(edge in edges) {
	var tasks = edges[edge]['nexttask'].split(',');
	for(e in tasks) {
		g.addEdge(null, edges[edge]['name'], tasks[e], {edgeclass: edges[edge]['status']});
	}
}

var renderer = new dagreD3.Renderer();
var oldDrawNodes = renderer.drawNodes();
renderer.drawNodes(function(graph, root) {
    var svgNodes = oldDrawNodes(graph, root);
    svgNodes.each(function(u) { d3.select(this).classed(graph.node(u).nodeclass, true); });
    return svgNodes;
  });
  var layout = renderer.run(g, d3.select("svg g"));
  d3.select("svg")
    .attr("width", layout.graph().width + 40)
    .attr("height", layout.graph().height + 40);

