function Islandviewer(ext_id) {
    this.ext_id = ext_id;
    console.log("Called constructor " + this.ext_id);
}

Islandviewer.prototype.onclick = function(trackname, d) {
    console.log("Got a callback " + d);
    console.log(trackname);
    console.log(d);
}

// Called by the brush update functions in the visualization
// objects (linear, circular)

Islandviewer.prototype.update = function(startBP, endBP) {

}

Islandviewer.prototype.update_finished = function(startBP, endBP) {
    url = '/islandviewer/json/genes/?ext_id=' + this.ext_id + '&start=' + parseInt(startBP) + '&end=' + parseInt(endBP);

    console.log(url);

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
			if(row.gi && row.gi !== 0) {
			    html += "class=\"";
			    gis = row.gi.split(',');
			    for(var i = 0; i < gis.length; i++) {
				html += "islandset_" + gis[i] + ' ';
			    }
			}
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
			    console.log("here " + row.name);
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
			html += "&nbsp;</td><td>" + row.gene + "</td><td>" + row.name + "</td><td>" + row.product + "</td></tr>";
		    }
		}
		html += "</table>";
		$('#gene_dialog').html(html);
	    }
	});
}

Islandviewer.prototype.mouseover = function(trackName, d) {
    if(trackName == 'circularGenes') {
	$('#gene_overlay_' + d.id).addClass("highlight_row");
    } else if((trackName == 'circularIslandpick') || (trackName == 'circularDimob') || (trackName == 'circularSigi')) {
	$('.islandset_' + d.id).addClass("highlight_row");
    }
}

Islandviewer.prototype.mouseout = function(trackName, d) {
    if(trackName == 'circularGenes') {
	$('#gene_overlay_' + d.id).removeClass("highlight_row");
    } else if((trackName == 'circularIslandpick') || (trackName == 'circularDimob') || (trackName == 'circularSigi')) {
	$('.islandset_' + d.id).removeClass("highlight_row");
    }
}
