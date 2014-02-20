from django.conf import settings
from django.http import HttpResponse
import csv
import xlwt
from Bio.SeqFeature import SeqFeature, FeatureLocation
import pprint

# Not used
def formatResults(resultset, format, methods):
    if format in formats:
        formats[format](resultset, methods, filename)
    else:
        raise Exception("Unknown format")
    
def formatCSV(resultset, methods, filename, delimiter=False):
    response = HttpResponse(content_type='text/csv')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    
    pprint.pprint(resultset)
    
    if delimiter:
        writer = csv.writer(response, delimiter=delimiter)
    else:
        writer = csv.writer(response)
    
    line = ["Island start", "Island end", "Length", "Method", "Gene name", "Gene ID", "Locus", "Gene start", "Gene end", "Strand", "Product"]
    writer.writerow(line)
    
    # Loop through again for integrated
    if 'integrated' in methods:
        for island in resultset:
            line = [island.island_start, island.island_end]
            line.append(int(island.island_end) - int(island.island_start))
            line += ["Predicted by at least one method", island.name, island.gene, island.locus, island.gene_start, island.gene_end, island.strand, island.product]
            writer.writerow(line)

    results_list = list(resultset)
    results_list.sort(key=lambda item:item.prediction_method)
    for island in results_list:
        if island.prediction_method.lower() in methods:
            line = [island.island_start, island.island_end]
            line.append(int(island.island_end) - int(island.island_start))
            method = methodfullnames[island.prediction_method.lower()]
            line += [method, island.name, island.gene, island.locus, island.gene_start, island.gene_end, island.strand, island.product]
            writer.writerow(line)
            
    return response

def formatGenbank(resultset, seqobj, methods, filename):
    response = HttpResponse(mimetype='plain/text')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    feature_offset = 0;
    
    # Loop through again for integrated
    if 'integrated' in methods:
        for island in resultset:
            seqobj.insertFeature(SeqFeature(FeatureLocation(island.start,island.end),
                                            type = "Misc", qualifiers={'note': 'Genomic Island: Predicted by at least one method'}), feature_offset)
            feature_offset += 1

    results_list = list(resultset)
    results_list.sort(key=lambda item:item.prediction_method)
    for island in results_list:
        if island.prediction_method.lower() in methods:
            seqobj.insertFeature(SeqFeature(FeatureLocation(island.start,island.end),
                                            type = "Misc", qualifiers={'note': 'Genomic Island: Predicted by ' + methodfullnames[island.prediction_method.lower()]}), feature_offset)
            feature_offset += 1

    seqobj.writeGenbank(response)
    
    return response

def formatFasta(resultset, seqobj, methods, filename):
    response = HttpResponse(mimetype='plain/text')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
   
    response.write(seqobj.generateFasta(seqtype = 'nuc', show_methods = True, methods = methods))
   
    return response

def formatTab(resultset, methods, filename):
    return formatCSV(resultset, methods, filename, '\t')

def formatExcel(resultset, methods, filename):
    response = HttpResponse(mimetype='application/ms-excel')
    response['Content-Disposition'] = 'attachment; filename="' + filename + '"'
    wb = xlwt.Workbook(encoding='utf-8')
    ws = wb.add_sheet("Islandviewer Results")

    row_num = 0
    
    font_style = xlwt.XFStyle()
    font_style.font.bold = True
    
    for col_num in xrange(len(excel_columns)):
        ws.write(row_num, col_num, excel_columns[col_num][0], font_style)
        # set column width
        ws.col(col_num).width = excel_columns[col_num][1]
        
    font_style = xlwt.XFStyle()
    font_style.alignment.wrap = 1
    
    # Loop through again for integrated
    if 'integrated' in methods:
        for island in resultset:
            row_num += 1
            island_size = int(island.island_end) - int(island.island_start)
            row = [
                   island.island_start,
                   island.island_end,
                   island_size,
                   "Predicted by at least one method",
                   island.name,
                   island.gene,
                   island.locus,
                   island.gene_start,
                   island.gene_end,
                   island.strand,
                   island.product
                   ]
            for col_num in xrange(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)

    results_list = list(resultset)
    results_list.sort(key=lambda item:item.prediction_method)
    for island in results_list:
        if island.prediction_method.lower() in methods:        
            row_num += 1
            island_size = int(island.island_end) - int(island.island_start)
            row = [
                   island.island_start,
                   island.island_end,
                   island_size,
                   methodfullnames[island.prediction_method.lower()],
                   island.name,
                   island.gene,
                   island.locus,
                   island.gene_start,
                   island.gene_end,
                   island.strand,
                   island.product
                   ]
            for col_num in xrange(len(row)):
                ws.write(row_num, col_num, row[col_num], font_style)
            
    wb.save(response)
    return response

    
excel_columns = [
    (u'Island start', 3000),
    (u'Island end', 3000),
    (u'Length', 2000),
    (u'Method', 8000),
    (u'Gene name', 6000),
    (u'Gene ID', 3000),
    (u'Locus', 4000),
    (u'Gene start', 3000),
    (u'Gene end', 3000),
    (u'Strand', 2000),
    (u'Product', 10000)
                 
]    

downloadformats = {'genbank': formatGenbank,
                   'fasta': formatFasta,
                   'tab': formatTab,
                   'csv': formatCSV,
                   'excel': formatExcel
}

downloadextensions = {'genbank': 'gbk',
                      'fasta': 'faa',
                      'tab': 'tsv',
                      'csv': 'csv',
                      'excel': 'xls'
}

methodfullnames = {'sigi': 'SIGI-HMM',
                   'dimob': 'IslandPath-DIMOB',
                   'islandpick': 'IslandPick'
                   
                   }
