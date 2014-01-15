var {{ plotName|default:"circular" }}data = [
{% comment %}Genes for linear view{% endcomment %}
	{ trackName: "{{ plotName|default:"circular" }}Genes",
	  trackType: "stranded",
	  inner_radius: 210,
	  outer_radius: 250,
	  visible: false,
	  items: [
		{% for gene in genes %}
		  {id: {{ gene.id }}, start: {{ gene.start }}, end: {{ gene.end }}, strand: {{ gene.strand }}, name: "{{ gene.name }}" },
		{% endfor %}
		]
	},
{% comment %}Islandpick track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Islandpick",
	  trackType: "track",
	  inner_radius: {{ ip_inner_radius|default:50 }},
	  outer_radius: {{ ip_outer_radius|default:100 }},
	  min_slice: true,
	  mouseover_callback: 'mouseoverIsland',
	  mouseout_callback: 'mouseoutIsland',
	  mouseclick: 'clickTrack',
	  items: [
	    {% for gi in gis %}
	       {% if gi.prediction_method == "Islandpick" %}{id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" },{% endif %}
	    {% endfor %}
	         ]
	 },
{% comment %}SIGI track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Sigi",
	  trackType: "track",
	  inner_radius: {{ sigi_inner_radius|default:100 }},
	  outer_radius: {{ sigi_outer_radius|default:150 }},
	  mouseover_callback: 'mouseoverIsland',
	  mouseout_callback: 'mouseoutIsland',
	  mouseclick: 'clickTrack',
	  items: [
	    {% for gi in gis %}
	       {% if gi.prediction_method == "Sigi" %}
	       {id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" },
	       {% endif %}
	    {% endfor %}
	         ]
	 },
{% comment %}Dimob track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Dimob",
	  trackType: "track",
	  inner_radius: {{ dimob_inner_radius|default:150 }},
	  outer_radius: {{ dimob_outer_radius|default:200 }},
	  min_slice: true,
	  mouseover_callback: 'mouseoverIsland',
	  mouseout_callback: 'mouseoutIsland',
	  mouseclick: 'clickTrack',
	  items: [
	    {% for gi in gis %}
	       {% if gi.prediction_method == "Dimob" %}
	       {id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" },
	       {% endif %}
	    {% endfor %}
	         ]
	 },
{% comment %}Integrated track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Integrated",
	  trackType: "track",
	  inner_radius: {{ int_inner_radius|default:215 }},
	  outer_radius: {{ int_outer_radius|default:250 }},
	  mouseover_callback: 'mouseoverIsland',
	  mouseout_callback: 'mouseoutIsland',
	  mouseclick: 'clickTrack',
	  skipLinear: true,
	  items: [
	    {% for gi in gis %}
	       {id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" },
	    {% endfor %}
	         ]
	 },
{% comment %}GC Plot track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}GCPlot",
	  trackType: "plot",
	  plot_radius: {{ gc_plot_radius|default:150 }},
	  plot_width: {{ gc_plot_width|default:75 }},
	  bp_per_element: {{ gc_bp_per_element|default:10000 }},
	  plot_min: {{ gc.min|default:0 }},
	  plot_max: {{ gc.max|default:0 }},
	  plot_mean: {{ gc.mean|default:0 }},
	  items: [
	          {{ gc.gc }}
	         ]
	 },
{% comment %}Virulence factor data{% endcomment %}
	{% if vir_factors %}
	{ trackName: "{{ plotName|default:"circular" }}Virulence",
	  trackType: 'glyph',
	  glyphType: '{{ virulenceShape|default:"circle" }}',
	  radius: {{ virulenceRadius|default:175 }},
	  pixel_spacing: 3,
	  glyph_buffer: 3,
	  glyphSize: 20,
	  items: [
	     {% for vir in vir_factors %}
	       {id: {{ forloop.counter }}, bp: {{ vir.0 }}, type: '{{ vir.1 }}'},
	     {% endfor %}
	         ]
	}{% endif %}
	];

var {{ plotName|default:"circular" }}layout = {genomesize: {{ genomesize }}, container: "{{ container }}", h: 500, w: 500 };
var {{ plotName|default:"circular" }}Track = new circularTrack({{ plotName|default:"circular" }}layout, {{ plotName|default:"circular" }}data);

var {{ plotName|default:"circular" }}Linearlayout = {genomesize: {{ genomesize }}, container: "{{ container }}linear", width: 600, height: 150};
var {{ plotName|default:"circular" }}LinearTrack = new genomeTrack({{ plotName|default:"circular" }}Linearlayout, {{ plotName|default:"circular" }}data);
{{ plotName|default:"circular" }}Track.attachBrush({{ plotName|default:"circular" }}LinearTrack);

function updateStrand(cb, strand) {
  track = '';

  switch(strand) {
  case "islandpick":
    track = "{{ plotName|default:"circular" }}Islandpick";
    break;
  case "sigi":
    track = "{{ plotName|default:"circular" }}Sigi";
    break;
  case "dimob":
    track = "{{ plotName|default:"circular" }}Dimob";
    break;
  case "integrated":
    track = "{{ plotName|default:"circular" }}Integrated";
    break;
  }

  if(cb.checked) {
    {{ plotName|default:"circular" }}Track.showTrack(track);
  } else {
    {{ plotName|default:"circular" }}Track.hideTrack(track);
  }
}

function updateVirulence(cb, vir_factor) {
  if(cb.checked) {
    {{ plotName|default:"circular" }}Track.showGlyphTrackType("{{ plotName|default:"circular" }}Virulence", vir_factor);
  } else {
    {{ plotName|default:"circular" }}Track.hideGlyphTrackType("{{ plotName|default:"circular" }}Virulence", vir_factor);
  }
}

function showHoverGenes(d) {

  $.getJSON('{% url 'genesjson' gi_id='00000' %}'.replace('00000', d.id), function(data) {
	  var tablediv = $('#geneslist');
	  var toshow; var tohide;
	  if(data.genes.length == 0) {
	    toshow = $("#geneslistnothing");
	    tohide = $("#geneslistvalues");
          } else {
	    toshow = $("#geneslistvalues");
	    tohide = $("#geneslistnothing");
	  }
	  if(tablediv.hasClass("hidden")) {
	    tablediv.removeClass("hidden").addClass("visible");
	  }
	  if(toshow.hasClass("hidden")) {
	    toshow.removeClass("hidden").addClass("visible");
	  }
	  if(tohide.hasClass("visible")) {
	    tohide.removeClass("visible").addClass("hidden");
	  }
	  geneList.fnClearTable();

	  geneList.fnAddData(data.genes);
      });
}

$('#genelistclose').click(function() {
  var tablediv = $('#geneslist');
  if(tablediv.hasClass("visible")) {
    tablediv.removeClass("visible").addClass("hidden");
  }
});

var popup_timer;
var popup_d;
function mouseoverIsland(d) {
  // Save the data object we received
  popup_d = d;
  popup_timer = setTimeout(function() {showHoverGenes(popup_d);}, 1000);
}

function mouseoutIsland(d) {
  clearTimeout(popup_timer);
}

function clickTrack(d) {
  clearTimeout(popup_timer);

  var half_range = (d.end - d.start)/2;
  {{ plotName|default:"circular" }}LinearTrack.update(Math.max(0,(d.start-half_range)), Math.min({{ genomesize }}, (d.end+half_range)));

  var wrapperdiv = $('#circularchartlinearwrapper');
  if(wrapperdiv.hasClass("hidden")) {
    wrapperdiv.removeClass("hidden").addClass("visible");
  }

  {{ plotName|default:"circular" }}Track.moveBrushbyBP(Math.max(0,(d.start-half_range)), 
                                                       Math.min({{ genomesize }}, (d.end+half_range)));

  {{ plotName|default:"circular" }}Track.showBrush();
  
  showHoverGenes(d);
}

$('#circularchartlinearclose').click(function() {
  var tablediv = $('#circularchartlinearwrapper');
  if(tablediv.hasClass("visible")) {
    tablediv.removeClass("visible").addClass("hidden");
  }

  {{ plotName|default:"circular" }}Track.hideBrush();

});

var geneList = $('#geneslisttable').dataTable({
	"bPaginate": false,
    "bLengthChange": false,
    "bFilter": false,
    "bSort": false,
    "bInfo": false,
    "bAutoWidth": false,
    "aoColumns": [
	{"mData": null, "bVisible": true},
	{"mData": "name", "bVisible": true},
	{"mData": "gene", "bVisible": true},
	{"mData": "locus", "bVisible": true},
	{"mData": "product", "bVisible": true},
	],
    "aoColumnDefs": [
	{ "aTargets": [0],
	  "mData": null,
	  "mRender": function(data, type, full) {
	               return full.start + ".." + full.end + "(" + full.strand + ")";
	             },
        }
      ]

});


function submit_download_form(output_format)
{
	// Get the d3js SVG element
	var html = d3.select("svg")
	.attr("title", "Islandviewer")
	.attr("version", 1.1)
        .attr("xmlns", "http://www.w3.org/2000/svg")
	.node().parentNode.innerHTML;
	var container = "{{ container }}".slice(1);

	var style = document.createElementNS("http://www.w3.org/1999/xhtml", "style");
	style.textContent += "<![CDATA[\n";
	// get stylesheet for svg
	// I have all svg styling in svg_elements.css
	for (var i=0;i<document.styleSheets.length; i++) {
	  str = document.styleSheets[i].href;
	  if (str.substr(str.length-16)=="islandviewer.css"){
      	    var rules = document.styleSheets[i].rules;
            for (var j=0; j<rules.length;j++){
             style.textContent += (rules[j].cssText + "\n");
            }
            break;
    	  }
        }
        style.textContent += "]]>";

	var tmp = document.getElementById(container);
	var clonedSVG = tmp.cloneNode(true);
	var svg = clonedSVG.getElementsByTagName("svg")[0];
	svg.getElementsByTagName("defs")[0].appendChild(style);
//	var $container = clonedSVG
	var $container = $('{{ container }}');
//	$container.getElementsByTagName("defs")[0].appendChild(style);
//	var html = container.html();
        // Canvg requires trimmed content

//        var content = $container.html().trim();
var content = clonedSVG.innerHTML.trim();
        //var canvas = document.getElementById('svg-canvas');
	var canvas = document.createElement('canvas');
    // Draw svg on canvas
    canvg(canvas, content);

    // Change img be SVG representation
    var theImage = canvas.toDataURL('image/png');
//console.log(theImage);
 //   $('#svg-img').attr('src', theImage);



//	var tmp = document.getElementById(container);
//	var svg = tmp.getElementsByTagName("svg")[0];
	// Extract the data as SVG text string
//	var svg_xml = (new XMLSerializer).serializeToString(svg);
//	console.log(typeof(svg_xml));
//        var imgData = 'data:image/svg+xml;base64,' + btoa(svg_xml);
//	var img = '<img src="'+imgData+'">';
//	d3.select("#svgdataurl").html(img);
//	var canvas = document.querySelector("canvas"),
//	    context = canvas.getContext("2d");
//	var image = new Image;
//	image.src = imgData;
//	image.onload = function() {
//	  context.drawImage(image, 0, 0);
//
	var blob = dataURLtoBlob(theImage);
//	var blob = new Blob([imgData], {type: "image/png"});
	console.log(blob);

	saveAs(blob, "img.png");
}

function dataURLtoBlob(dataURL) {
  // Decode the dataURL    
  var binary = atob(dataURL.split(',')[1]);
  // Create 8-bit unsigned array
  var array = [];
  for(var i = 0; i < binary.length; i++) {
      array.push(binary.charCodeAt(i));
  }
  // Return our Blob object
  return new Blob([new Uint8Array(array)], {type: 'image/png'});
}

//Encode the SVG
$("#save_as_png").click(function() { submit_download_form("png"); });
var serializer = new XMLSerializer();
var xmlString = serializer.serializeToString(d3.select('svg').node());
var imgData = 'data:image/svg+xml;base64,' + btoa(xmlString);

