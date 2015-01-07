function Islandviewer(aid, ext_id, genomesize, genomename, trackdata) {
    this.aid = aid;
    this.ext_id = ext_id;
    this.genomesize = genomesize;
    this.genomename = genomename;
    this.trackdata = trackdata;
    console.log("Called constructor " + this.ext_id + ' ' + genomename);
}

Islandviewer.prototype.addCircularPlot = function(layout) {
    this.circularplot = new circularTrack(layout, this.trackdata);

    return this.circularplot;
}

Islandviewer.prototype.addLinearPlot = function(layout) {
    this.linearplot = new genomeTrack(layout, this.trackdata);

    return this.linearplot;
}

Islandviewer.prototype.onclick = function(trackname, d, plotid) {
//    console.log("Got a callback " + d);
//    console.log(trackname);
//    console.log(d);
//    console.log(plotid);

    if(plotid == 'circularchartlinear') {

      if(trackname == 'circularVirulence') {
	var url = false;

        if(d.type == "VFDB") {
          url = 'http://www.mgc.ac.cn/cgi-bin/VFs/vfs.cgi?VFID=' + d.name;

        } else if(d.type == 'PATRIC_VF') {
          url = 'http://patricbrc.org/portal/portal/patric/Feature?cType=feature&cId=' + d.name;
	} else if(d.type == 'Victors') {
	  url = 'http://www.phidias.us/victors/gene_detail.php?c_mc_victor_id=' + d.name;
	} else if(d.type == 'CARD') {
	  url = 'http://arpcard.mcmaster.ca/?q=CARD/ontology/' + d.name
	} else if(d.type == 'RGI') {
	  url = 'http://arpcard.mcmaster.ca/?q=CARD/ontology/' + d.name
	}

	// Open the link if we've found something
	if(url) {
	  window.open(url);
	}
      } else if(trackname == 'circularGenes') {
        var url = 'http://www.ncbi.nlm.nih.gov/protein/' + d.accnum;

        window.open(url);
      } else if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi')) {

//        var view_start = Math.max(0, (d.start-500));
//	var view_end = Math.min((d.end+500), this.genomesize);
	$('.method_row').each(function() {
	    $(this).removeClass('highlightrow')
	});
	$('html, body').animate({ scrollTop: $('#table_' + d.id).offset().top }, 'slow');
	$("#table_" + d.id).addClass('highlightrow');

//	var url = 'http://www.ncbi.nlm.nih.gov/projects/sviewer/?id=' + this.ext_id + '&v=' + view_start + '..' + view_end + '&m=' + d.start + ',' + d.end;
//	window.open(url);
      }
    } else if(plotid == 'circularchart') {

      if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi') || (trackname == 'circularIntegrated')) {
        clearTimeout(this.popup_timer);

        var half_range = (d.end - d.start)/2;
        this.linearplot.update(Math.max(0,(d.start-half_range)), Math.min(this.genomesize, (d.end+half_range)));

        this.circularplot.moveBrushbyBP(Math.max(0,(d.start-half_range)), 
                                                       Math.min(this.genomesize, (d.end+half_range)));

        this.circularplot.showBrush();
  
        this.showHoverGenes(d, true);

      }
    }
}

Islandviewer.prototype.mouseover = function(trackname, d, plotid) {
//    console.log("Got a callback " + d);
//    console.log(trackname);
//    console.log(d);
//    console.log(plotid);

    if(plotid == 'circularchartlinear') {
      if(trackname == 'circularGenes') {
  	$('#gene_overlay_' + d.id).addClass("highlight_row");
      } else if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi')) {
	$('.islandset_' + d.id).addClass("highlight_row");
      } else if(trackname == 'circularVirulence') {
        $('.gene_' + d.gene.replace('.', '')).addClass("highlight_row");
      }

    } else if (plotid == 'circularchart') {
      if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi') || (trackname == 'circularIntegrated')) {

        this.popup_d = d;
//        this.popup_timer = setTimeout(function() {this.showHoverGenes(popup_d);}, 1000, [d, this]);
        this.popup_timer = setTimeout(this.showHoverGenes.bind(this), 1000, this.popup_d, false);
      }
    }
}

Islandviewer.prototype.mouseout = function(trackname, d, plotid) {
//    console.log("mouseout callback " + d);
//    console.log(trackname);
//    console.log(d);
//    console.log(plotid);

    if(plotid == 'circularchartlinear') {
      if(trackname == 'circularGenes') {
  	$('#gene_overlay_' + d.id).removeClass("highlight_row");
      } else if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi')) {
	$('.islandset_' + d.id).removeClass("highlight_row");
      } else if(trackname == 'circularVirulence') {
        $('.gene_' + d.gene.replace('.', '')).removeClass("highlight_row");
      }

    } else if (plotid == 'circularchart') {
      if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi') || (trackname == 'circularIntegrated')) {
        clearTimeout(this.popup_timer);
      }

    }
}

// Called by the brush update functions in the visualization
// objects (linear, circular)

Islandviewer.prototype.update = function(startBP, endBP) {

}

Islandviewer.prototype.update_finished = function(startBP, endBP) {
    url = '../../json/genes/?aid=' + this.aid + '&ext_id=' + this.ext_id + '&start=' + parseInt(startBP) + '&end=' + parseInt(endBP);
    self = this;

//        console.log(url);

    $.ajax({
	    url: url,
	    type: "get",
	    success: function(data) {
		var html = "<table class=\"genespopup\"><tr><th>Prediction Method</th><th>Gene Name</th><th>Accnum</th><th>Product</th></tr>";
		genes = data.genes
		for(var gene in genes) {
		    if(genes.hasOwnProperty(gene)) {
			row = genes[gene];
			html += "<tr id=\"gene_overlay_" + row.geneid + "\" ";
			html += "class=\"";
			if(row.gi && row.gi !== 0) {
			    gis = row.gi.split(',');
			    for(var i = 0; i < gis.length; i++) {
				html += "islandset_" + gis[i] + ' ';
			    }
			}
			html += 'gene_' + row.name.replace('.', '') + ' ';
			html += "\"><td>";
//			console.log(row);
			if(row.method && row.method !== 0) {
			    methods = row.method.split(',');
			    if($.inArray('Islandpick', methods) >= 0) {
				html += "<span class=\"islandbox greenislandbox\">&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('Sigi', methods) >= 0) {
				html += "<span class=\"islandbox orangeislandbox\">&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('Dimob', methods) >= 0) {
				html += "<span class=\"islandbox blueislandbox\">&nbsp;&nbsp;</span>";
			    }
			}
			if(row.virulence && row.virulence !== 0) {
			    virulence = row.virulence.split(',');
			    if($.inArray('ARDB', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_ARDB\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('CARD', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_CARD\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('VFDB', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_VFDB\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('PAG', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_PAG\">&nbsp;</span>";
			    }
			    if($.inArray('RGI', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_RGI\">&nbsp;</span>";
			    }
			    if($.inArray('Victors', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_Victors\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('PATRIC_VF', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_PATRIC_VF\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('BLAST', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_BLAST\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			}

			var gene_name = row.locus;
			if(row.gene) {
			    gene_name = row.gene;
			}
			html += "&nbsp;</td><td>" + gene_name + "</td><td><a href=\"http://www.ncbi.nlm.nih.gov/protein/" + row.name + "\" target=\"_blank\">" + row.name + "</a></td><td>" + row.product + "</td></tr>";
		    }
		}
		html += "</table>";
		$('#gene_dialog').html(html);
                $('#gene_dialog').dialog('option', 'title', 'Genes (' + self.genomename + ')');

	    }
	});
}

Islandviewer.prototype.showHoverGenes = function(d, do_half_range) {

  var half_range = typeof do_half_range !== 'undefined' ? (d.end - d.start)/2 : 0;

  $('#gene_dialog').dialog("open");
  this.update_finished(Math.max(0,(d.start-half_range)), Math.min(this.genomesize, (d.end+half_range)));
}

Islandviewer.prototype.scrollandOpen = function(d) {
	var self = this;
	$("html, body").animate({ scrollTop: 0 }, 'slow').promise().done( function() {
	  self.showHoverGenes(d);
	});
}

Islandviewer.prototype.findMethods = function() {

    if('undefined' === typeof this.types) {
      var types = {};

      // Loop through the data and find all methods
      for(var i=0; i < this.trackdata.length; i++) {
        if(this.trackdata[i].trackName == "circularIslandpick" || 
           this.trackdata[i].trackName == "circularSigi" || 
           this.trackdata[i].trackName == "circularDimob") {

           if(this.trackdata[i].items.length > 0) {
             types[ this.trackdata[i].trackName] = true;
           }
        } else if(this.trackdata[i].trackName == "circularVirulence") {
          items = this.trackdata[i].items;
          for(var j=0; j < items.length; j++) {
            if(!(items[j].type in types)) {
              types[items[j].type] = true;
            }
          }
        }
      }

      this.types = types;
    }

    return this.types;
}

Islandviewer.prototype.showIslandpickGenomes = function(aid) {
    url = '../../json/islandpick/' + aid + '/';
    self = this;

//        console.log(url);

    $.ajax({
	    url: url,
	    type: "get",
	    success: function(data) {
    	        $('#gene_dialog').dialog("open");
		var html = '';
		if((typeof data['default_analysis'] !== 'undefined') && !JSON.parse(data['default_analysis'])) {
			html += '<blockquote style=\"border-left: none;\"><span class="errortext">The genomes used to run IslandPick in this analysis were not the default selections by our algorithm.</span></blockquote>'
		} else {
			html += "<blockquote style=\"border-left: none;\"><p class=\"smalltext\">IslandPick results are highly dependent on the comparison genomes selected. The following list of genomes were selected by default. The default selection is provided as a starting point and can be customized (particularly if you do not see any results, or to choose comparison genomes associated with a certain phenotype or phylogenetic distance). To run a customized IslandPick analysis, follow the link below to select a different set of comparison genomes. You are welcome to contact us if you would like more help.</p>";
		}
		genomes = data.genomes
		if(typeof data['nogenomesselected'] !== 'undefined' && JSON.parse(data['nogenomesselected'])) {
//		if(objectSize(genomes) == 0) {
			html += "<span class=\"errortext\">No candidate comparison genomes were found with the default settings.</span><br />&nbsp;<br />";
		} else {
			html += "</blockquote><ul class=\"genespopup\">\n";
			for(var cid in genomes) {
			    genome = genomes[cid];
	
			    if((typeof genome['used'] === 'undefined') || !JSON.parse(genome['used'])) {
			        continue;
			    }
			    html += '<li><a href="../../accession/' + cid + '/">' + genome['name'] + '(' + genome['dist'] + ')</a></li>\n';
	                }
			html += '</ul><blockquote style=\"border-left: none;\">'
		}
		html += "<a class=\"genespopup\" href=\"../../islandpick/select/" + aid + "/\" >[ Change comparison genomes ]</a></blockquote><br />&nbsp;<br />";

		$('#gene_dialog').html(html);
                $('#gene_dialog').dialog('option', 'title', 'Comparison Genomes');
	     }
     });
}

function objectSize(the_object) {
	  /* function to validate the existence of each key in the object to get the number of valid keys. */
	  var object_size = 0;
	  for (key in the_object){
	    if (the_object.hasOwnProperty(key)) {
	      object_size++;
	    }
	  }
	  return object_size;
	}

