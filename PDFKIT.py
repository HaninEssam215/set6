import pdfkit

path_to_file = 'invoice.html'


options = {
    'page-width': '8.27in', 
    'page-height': '11.69in', 
    'dpi': 100,
    'margin-top': '0',
    'margin-right': '0',
    'margin-bottom': '0',
    'margin-left': '0',
    'enable-local-file-access': True,
}

pdfkit.from_file(path_to_file, 'invoice_output.pdf', options=options)