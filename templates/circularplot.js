var {{ plotName|default:"circular" }}data = [
{% comment %}Genes for linear view{% endcomment %}
	{ trackName: "{{ plotName|default:"circular" }}Genes",
	  trackType: "stranded",
	  inner_radius: 210,
	  outer_radius: 250,
	  visible: false,
	  showLabels: true,
	  showTooltip: true,
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'clickGene',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
	  items: [
		{% for gene in genes %}
		  {id: {{ gene.id }}, start: {{ gene.start }}, end: {{ gene.end }}, strand: {{ gene.strand }}, name: "{{ gene.locus }}", accnum: "{{ gene.name }}" },
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
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'clickIsland',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
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
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'clickIsland',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
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
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'clickIsland',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
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
          linear_pixel_spacing: 6,
	  glyph_buffer: 3,
	  linear_glyph_buffer: 6,
	  glyphSize: 20,
	  linear_glyphSize: 30,
          linear_padding: 4,
          linear_height: 5,
          linear_invert: true,
	  showTooltip: true,
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
	  items: [
	     {% for vir in vir_factors %}
	       {id: {{ forloop.counter }}, bp: {{ vir.0 }}, type: '{{ vir.1 }}', name: '{{ vir.2 }}'},
	     {% endfor %}
	         ]
	}{% endif %}
];

var {{ plotName|default:"circular" }}layout = {genomesize: {{ genomesize }}, container: "{{ container }}", h: 500, w: 500, ExtraWidthX: 55, TranslateX: 25, ExtraWidthY: 40, TranslateY: 20 };
var {{ plotName|default:"circular" }}Track = new circularTrack({{ plotName|default:"circular" }}layout, {{ plotName|default:"circular" }}data);

$('#loadingimg').remove();

var {{ plotName|default:"circular" }}Linearlayout = {genomesize: {{ genomesize }}, container: "{{ container }}linear", width: 600, height: 135, bottom_margin:0};
var {{ plotName|default:"circular" }}LinearTrack = new genomeTrack({{ plotName|default:"circular" }}Linearlayout, {{ plotName|default:"circular" }}data);
{{ plotName|default:"circular" }}Track.attachBrush({{ plotName|default:"circular" }}LinearTrack);
{{ plotName|default:"circular" }}LinearTrack.addBrushCallback({{ plotName|default:"circular" }}Track);

var islandviewerObj = new Islandviewer('{{ext_id}}');
{{ plotName|default:"circular" }}Track.attachBrush(islandviewerObj);
{{ plotName|default:"circular" }}LinearTrack.addBrushCallback(islandviewerObj);

$('#gene_dialog').dialog( { position: { my: "left top", at: "right top", of: "{{ container }}_svg" },
	                    height: 550, width: 450,
			    title: "Genes",
			    autoOpen: false } );

function updateStrand(cb, strand) {
  var track = '';

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

function showHoverGenes(d, do_half_range) {

  var half_range = typeof do_half_range !== 'undefined' ? (d.end - d.start)/2 : 0;

  $('#gene_dialog').dialog("open");
  islandviewerObj.update_finished(Math.max(0,(d.start-half_range)), Math.min({{ genomesize }}, (d.end+half_range)));
}

function showIslandGenes(d) {

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

  var wrapperdiv = $('#circularchartlinearwrapper');
  if(wrapperdiv.hasClass("hidden")) {
    wrapperdiv.removeClass("hidden").addClass("visible");
  }

  var half_range = (d.end - d.start)/2;
  {{ plotName|default:"circular" }}LinearTrack.update(Math.max(0,(d.start-half_range)), Math.min({{ genomesize }}, (d.end+half_range)));

  {{ plotName|default:"circular" }}Track.moveBrushbyBP(Math.max(0,(d.start-half_range)), 
                                                       Math.min({{ genomesize }}, (d.end+half_range)));

  {{ plotName|default:"circular" }}Track.showBrush();
  
//  showIslandGenes(d);

  showHoverGenes(d, true);

}

window.onload = function() {
  var wrapperdiv = $('#circularchartlinearwrapper');
  if(wrapperdiv.hasClass("linear_hidden")) {
    wrapperdiv.removeClass("linear_hidden").addClass("hidden");
  }

  {{ plotName|default:"circular" }}Track.hideBrush();

  for(var i=0; i < {{ plotName|default:"circular" }}data.length; i++) {
    if({{ plotName|default:"circular" }}data[i].trackName == "{{ plotName|default:"circular" }}Integrated") {
      if({{ plotName|default:"circular" }}data[i].items.length > 0) {
        item = {{ plotName|default:"circular" }}data[i].items[0];
	var wrapperdiv = $('#circularchartlinearwrapper');
        if(wrapperdiv.hasClass("hidden")) {
        wrapperdiv.removeClass("hidden").addClass("visible");
      }

      var half_range = (item.end - item.start)/2;
      {{ plotName|default:"circular" }}LinearTrack.update(Math.max(0,(item.start-half_range)), Math.min({{ genomesize }}, (item.end+half_range)));
//      {{ plotName|default:"circular" }}LinearTrack.update(2840000,2905000);

      {{ plotName|default:"circular" }}Track.moveBrushbyBP(Math.max(0,(item.start-half_range)), 
                                                       Math.min({{ genomesize }}, (item.end+half_range)));

      {{ plotName|default:"circular" }}Track.showBrush();

      islandviewerObj.update_finished(Math.max(0,(item.start-half_range)), Math.min({{ genomesize }}, (item.end+half_range)));
      }
    }
  }


};


function clickGene(d) {
	var url = 'http://www.ncbi.nlm.nih.gov/protein/' + d.accnum;

	window.open(url);
}

function clickIsland(d) {
	var view_start = Math.max(0, (d.start-500));
	var view_end = Math.min((d.end+500), {{genomesize|default_if_none:"0"}});
	var url = 'http://www.ncbi.nlm.nih.gov/projects/sviewer/?id={{ ext_id|default_if_none:"nothing" }}&v=' + view_start + '..' + view_end + '&m=' + d.start + ',' + d.end;

	window.open(url);
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


function feature_tour() {
//                 $('#gene_dialog').dialog("open");
	var intro = introJs();
	var dialog_was_open = false;
        $('#download_dialog').removeClass("hidden");
        if($('#gene_dialog').dialog( "isOpen" ) === false) {
          $('#gene_dialog').dialog("open");
          dialog_was_open = false;
        } else {
          dialog_was_open = true;
        }
        intro.onexit(function() {
          if(dialog_was_open === false) {
	    $('#gene_dialog').dialog( "close" );
          }
          $('#download_dialog').addClass("hidden");
        });

        intro.oncomplete(function() {
          if(dialog_was_open === false) {
	    $('#gene_dialog').dialog( "close" );
          }
          $('#download_dialog').addClass("hidden");
        });

	intro.setOptions({
	  showStepNumbers: false,
	  steps: [
	    {
	      element: document.querySelector('{{ container }}'),
	      intro: "<b>Circular viewer</b><br />In the circular viewer you can click on islands to zoom the linear viewer to a location and pop up a context list of genes and islands.<br />&nbsp;<br />The black circular markers can be use to refocus and zoom the linear viewer.<br />&nbsp;<br />And the plot can be resized using the drag bar in the lower right corner.",
	      position: 'right'
	    },
	    {
	      element: '{{ container }}linear',
	      intro: "<b>Linear viewer</b><br />In the linear viewer you can zoom and scroll using your mouse and mousewheel respectively. Clicking on a gene will take you to the NCBI gene card and clicking on an island will take you the the NCBI genome viewer for that bp range.<br />&nbsp;<br />Hovering over elements will highlight the corresponding gene(s) in the gene dialog.<br />&nbsp;<br />And the plot can be resized using the drag bar on the right side.",
	      position: 'top'
	    },
	    {
	      element: '#gene_dialog',
	      intro: "<b>Gene list</b><br />The gene dialog will show all the genes in the range currently visible in the linear viewer.  Islands and virulence factors are displayed by colour coded glyphs.<br />&nbsp;<br />The dialog may be resized and moved using your mouse.",
	      position: 'left'
	    },
	    {
	      element: document.querySelector('#legend'),
	      intro: "<b>Legend</b><br />Individual tracks can be turned on and off using legend, they will be dynamically added/removed from the circular viewer.",
	      position: 'right'
	    },
	    {
	      element: document.querySelector('#download_container'),
	      intro: "<b>Download dialog</b><br />Results and the circular viewer can be downloaded via the download dialog, click to expand it.",
	      position: 'top'
	    }
	  ]
	});

	intro.start();
}

function submit_download_form(output_format, basefilename)
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
	  if (str.substr(str.length-14)=="islandplot.css"){
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

	if(output_format == 'svg') {
//	    hrefobj.attr("href", "data:image/svg+xml;base64," + btoa(content))
	    var a = document.createElement('a');
	console.log(content);
	    a.href = "data:application/octet-stream;base64;attachment," + btoa(content);
	    a.download = basefilename + ".svg";
	    a.click();
//	    window.open("data:application/octet-stream;base64;attachment;filename=\"img.svg\"," + btoa(content));
	    return;
	}
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
//	console.log(blob);

	saveAs(blob, basefilename + ".png");
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

