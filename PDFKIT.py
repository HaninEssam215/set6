import pdfkit

path_to_file = 'reminder.html'


options = {
    'page-width': '8.27in',  # Set the width to 8.27 inches
    'page-height': '11.69in',  # Set the height to 11.69 inches
    # 'page-size': 'A4',
    'dpi': 100,
    'margin-top': '0',
    'margin-right': '0',
    'margin-bottom': '0',
    'margin-left': '0',
    'enable-local-file-access': True,
}

pdfkit.from_file(path_to_file, 'reminder_output.pdf', options=options)