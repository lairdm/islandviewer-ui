function Islandviewer(ext_id, genomesize, genomename) {
    this.ext_id = ext_id;
    this.genomesize = genomesize;
    this.genomename = genomename;
    console.log("Called constructor " + this.ext_id + ' ' + genomename);
}

Islandviewer.prototype.addCircularPlot = function(layout, data) {
    this.circularplot = new circularTrack(layout, data);

    return this.circularplot;
}

Islandviewer.prototype.addLinearPlot = function(layout, data) {
    this.linearplot = new genomeTrack(layout, data);

    return this.linearplot;
}

Islandviewer.prototype.onclick = function(trackname, d, plotid) {
    console.log("Got a callback " + d);
    console.log(trackname);
    console.log(d);
    console.log(plotid);

    if(plotid == 'circularchartlinear') {

      if(trackname == 'circularVirulence') {
        if(d.type == "VFDB") {
          var url = 'http://www.mgc.ac.cn/cgi-bin/VFs/vfs.cgi?VFID=' + d.name;

	  window.open(url);
        }
      } else if(trackname == 'circularGenes') {
        var url = 'http://www.ncbi.nlm.nih.gov/protein/' + d.accnum;

        window.open(url);
      } else if((trackname == 'circularIslandpick') || (trackname == 'circularDimob') || (trackname == 'circularSigi')) {

        var view_start = Math.max(0, (d.start-500));
	var view_end = Math.min((d.end+500), this.genomesize);
	var url = 'http://www.ncbi.nlm.nih.gov/projects/sviewer/?id=' + this.ext_id + '&v=' + view_start + '..' + view_end + '&m=' + d.start + ',' + d.end;

	window.open(url);
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
    console.log("Got a callback " + d);
    console.log(trackname);
    console.log(d);
    console.log(plotid);

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
	console.log("timing!");
        this.popup_d = d;
//        this.popup_timer = setTimeout(function() {this.showHoverGenes(popup_d);}, 1000, [d, this]);
        this.popup_timer = setTimeout(this.showHoverGenes.bind(this), 1000, this.popup_d, false);
      }
    }
}

Islandviewer.prototype.mouseout = function(trackname, d, plotid) {
    console.log("mouseout callback " + d);
    console.log(trackname);
    console.log(d);
    console.log(plotid);

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
    url = '/islandviewer/json/genes/?ext_id=' + this.ext_id + '&start=' + parseInt(startBP) + '&end=' + parseInt(endBP);
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
			    if($.inArray('VFDB', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_VFDB\">&nbsp;&nbsp;&nbsp;</span>";
			    }
			    if($.inArray('PAG', virulence) >= 0) {
				html += "<span class=\"virulencecircle virulencecircle_PAG\">&nbsp;</span>";
			    }
			}

			html += "&nbsp;</td><td>" + row.gene + "</td><td><a href=\"http://www.ncbi.nlm.nih.gov/protein/" + row.name + "\" target=\"_blank\">" + row.name + "</a></td><td>" + row.product + "</td></tr>";
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

