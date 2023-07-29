from jinja2 import Template
import pdfkit

path_to_file = 'invoice.html'

# Your data (variables)
data = {
    "LOGO": "HANIN",
    "current_page": 1,
    "number_pages": 5,
    # Add more variables here...
}

# Read the HTML template from file
with open("invoice.html", "r") as file:
    template_content = file.read()

# Create a Jinja2 template object
template = Template(template_content)

# Render the template with the provided data
rendered_html = template.render(data)

# Now, you can use the 'rendered_html' as needed, for example, send it in a response or save to a file.

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

pdfkit.from_string(rendered_html, 'invoice_output_var.pdf', options=options)