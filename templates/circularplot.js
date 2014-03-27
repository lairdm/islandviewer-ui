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
	  linear_mouseclick: 'islandviewerObj',{% endif %}
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
	  mouseover_callback: 'islandviewerObj',
	  mouseout_callback: 'islandviewerObj',
	  mouseclick: 'islandviewerObj',
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'islandviewerObj',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
	  items: [
	    {% for gi in gis %}
	       {% if gi.prediction_method == "Islandpick" %}{id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" }{% if not forloop.last %},{% endif %}{% endif %}
	    {% endfor %}
	         ]
	 },
{% comment %}SIGI track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Sigi",
	  trackType: "track",
	  inner_radius: {{ sigi_inner_radius|default:100 }},
	  outer_radius: {{ sigi_outer_radius|default:150 }},
	  mouseover_callback: 'islandviewerObj',
	  mouseout_callback: 'islandviewerObj',
	  mouseclick: 'islandviewerObj',
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'islandviewerObj',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
	  items: [
	    {% for gi in gis %}
	       {% if gi.prediction_method == "Sigi" %}
	       {id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" }{% if not forloop.last %},{% endif %}
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
	  mouseover_callback: 'islandviewerObj',
	  mouseout_callback: 'islandviewerObj',
	  mouseclick: 'islandviewerObj',
	  {% if ext_id %}ext_id: '{{ext_id}}',
	  linear_mouseclick: 'islandviewerObj',{% endif %}
	  linear_mouseover: 'islandviewerObj',
	  linear_mouseout: 'islandviewerObj',
	  items: [
	    {% for gi in gis %}
	       {% if gi.prediction_method == "Dimob" %}
	       {id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" }{% if not forloop.last %},{% endif %}
	       {% endif %}
	    {% endfor %}
	         ]
	 },
{% comment %}Integrated track data{% endcomment %}
        { trackName: "{{ plotName|default:"circular" }}Integrated",
	  trackType: "track",
	  inner_radius: {{ int_inner_radius|default:215 }},
	  outer_radius: {{ int_outer_radius|default:250 }},
	  mouseover_callback: 'islandviewerObj',
	  mouseout_callback: 'islandviewerObj',
	  mouseclick: 'islandviewerObj',
	  skipLinear: true,
	  items: [
	    {% for gi in gis %}
	       {id: {{ gi.gi }}, start: {{ gi.start }}, end: {{ gi.end }}, name: "{{ gi.gi }}" }{% if not forloop.last %},{% endif %}
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
          linear_mouseclick: 'islandviewerObj',
	  items: [
	     {% for vir in vir_factors %}
	       {id: {{ forloop.counter }}, bp: {{ vir.start }}, type: '{{ vir.source }}', name: '{{ vir.external_id }}', gene: '{{ vir.name }}'}{% if not forloop.last %},{% endif %}
	     {% endfor %}
	         ]
	}{% endif %}
];

var islandviewerObj = new Islandviewer('{{ext_id}}', {{ genomesize|default:"0" }});

var {{ plotName|default:"circular" }}layout = {genomesize: {{ genomesize }}, container: "{{ container }}", h: 500, w: 500, ExtraWidthX: 55, TranslateX: 25, ExtraWidthY: 40, TranslateY: 20 };
//var {{ plotName|default:"circular" }}Track = new circularTrack({{ plotName|default:"circular" }}layout, {{ plotName|default:"circular" }}data);
var {{ plotName|default:"circular" }}Track = islandviewerObj.addCircularPlot({{ plotName|default:"circular" }}layout, {{ plotName|default:"circular" }}data);

$('#loadingimg').remove();

var {{ plotName|default:"circular" }}Linearlayout = {genomesize: {{ genomesize }}, container: "{{ container }}linear", width: 600, height: 135, bottom_margin:0};
//var {{ plotName|default:"circular" }}LinearTrack = new genomeTrack({{ plotName|default:"circular" }}Linearlayout, {{ plotName|default:"circular" }}data);
var {{ plotName|default:"circular" }}LinearTrack = islandviewerObj.addLinearPlot({{ plotName|default:"circular" }}Linearlayout, {{ plotName|default:"circular" }}data);

{{ plotName|default:"circular" }}Track.attachBrush({{ plotName|default:"circular" }}LinearTrack);
{{ plotName|default:"circular" }}LinearTrack.addBrushCallback({{ plotName|default:"circular" }}Track);

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

// Old island genes table below the linear view, not used anymore
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

// Old island genes table below the linear view, not used anymore
$('#genelistclose').click(function() {
  var tablediv = $('#geneslist');
  if(tablediv.hasClass("visible")) {
    tablediv.removeClass("visible").addClass("hidden");
  }
});

var popup_timer;
var popup_d;

window.onload = function() {
//  var wrapperdiv = $('#circularchartlinearwrapper');
//  if(wrapperdiv.hasClass("linear_hidden")) {
//    wrapperdiv.removeClass("linear_hidden").addClass("hidden");
//  }

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


$('#circularchartlinearclose').click(function() {
  var tablediv = $('#circularchartlinearwrapper');
  if(tablediv.hasClass("visible")) {
    tablediv.removeClass("visible").addClass("hidden");
  }

  {{ plotName|default:"circular" }}Track.hideBrush();

});

// Old genes list table below the linear view, no longer used
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
	      intro: "<b>Circular viewer</b><br />In the circular viewer you can click on islands to zoom the linear viewer below to a location and pop up a context list of genes and islands.<br />&nbsp;<br />The black circular markers can be dragged to refocus and zoom the linear viewer.<br />&nbsp;<br />The plot can be resized using the drag bar in the lower right corner.",
	      position: 'right'
	    },
	    {
	      element: '{{ container }}linear',
	      intro: "<b>Linear viewer</b><br />In the linear viewer you can zoom and scroll using your mouse and mousewheel respectively (or use two fingers on your touch pad depending on your device).<br />&nbsp;<br />Hovering over elements will highlight the corresponding gene(s) in the gene dialog.<br />&nbsp;<br />Clicking on a gene will take you to the NCBI gene card and clicking on an island will take you the the NCBI genome viewer for that bp range.<br />&nbsp;<br />The plot can be resized using the drag bar on the right side.",
	      position: 'top'
	    },
	    {
	      element: '#gene_dialog',
	      intro: "<b>Gene list</b><br />The gene dialog will show all the genes in the range currently visible in the linear viewer, and bounded by the shaded region bounded by the black circles in the circular viewer. Islands, virulence factors, etc are marked with colour coded glyphs.<br />&nbsp;<br />The dialog may be resized and moved using your mouse.",
	      position: 'left'
	    },
	    {
	      element: document.querySelector('#legend'),
	      intro: "<b>Legend</b><br />Individual tracks can be turned on and off using legend. They will be dynamically added/removed from the circular viewer.",
	      position: 'right'
	    },
	    {
	      element: document.querySelector('#download_container'),
	      intro: "<b>Download dialog</b><br />Results and the circular viewer can be downloaded via the download dialog, click to expand it.",
	      position: 'top'
	    },
	    {
	      element: document.querySelector('#gitableheader'),
	      intro: "<b>Genomic Islands table</b><br />Below is a summary of results grouped by detection method.",
	      position: 'top'
	    },
	    {
	      element: document.querySelector('#legend_help'),
	      intro: "<b>More questions?</b><br />For more information see our help page and our FAQ, if you still have questions don't hesitate to contact us.",
	      position: 'top'
	    }
	  ]
	});

	intro.start();
}


