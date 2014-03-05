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
			html += "<tr><td>"
			if(row.method && row.method !== 0) {
			    methods = row.method.split(',');
			console.log(methods);
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
			html += "&nbsp;</td><td>" + row.gene + "</td><td>" + row.name + "</td><td>" + row.product + "</td></tr>";
		    }
		}
		html += "</table>";
		$('#gene_dialog').html(html);
	    }
	});
}