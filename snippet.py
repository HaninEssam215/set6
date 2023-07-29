from jinja2 import Environment, FileSystemLoader
from django.core.files.storage import default_storage
from django.core.files.base import ContentFile
from io import BytesIO
import math
from PyPDF2 import PdfMerger
import pdfkit
import base64
import mimetypes
from django.db.models import F
from django.apps import apps


def create_invoice_pdf(**kwargs):
    rows_per_page = 3
    rows_last_page = 1  
    
    
    env = Environment(loader=FileSystemLoader('core/templates/pdf_templates/invoices'))
    pdf_invoice_template = env.get_template(f"{kwargs.get('template_name')}.html")

    # Read the image file
    if kwargs.get('path_to_logo'):
        logo_file = default_storage.open(kwargs.get('path_to_logo'), 'rb')
        # Convert the image file to a base64 string
        logo_base64 = base64.b64encode(logo_file.read()).decode()
        # Get the content type of the image
        content_type = mimetypes.guess_type(company.logo.url)[0]
        # Create a data URL with the base64 string
        logo_path = f"data:{content_type};base64,{logo_base64}"  # necessary for wkhtmltool to read it properly
    else: 
        logo_path = None

    invoice_setting = InvoiceSetting.objects.get(company=company)
    rows = kwargs.get('rows', [])
    
    if kwargs.get('period_start') and kwargs.get('period_end'): 
        invoice_period = f"{kwargs.get('period_start')} - {kwargs.get('period_end')}"
    else: 
        invoice_period = None

    # Define a dictionary that maps fields to their values
    all_fields = {
        'invoice_text': kwargs.get('invoice_text', None),
        'terms_of_payment': kwargs.get('terms_of_payment', None),
        'late_interest_rate': kwargs.get('late_interest_rate', None),
        'your_reference': kwargs.get('your_reference', None),
        'our_reference': kwargs.get('our_reference', None),
        'buyers_order_number': kwargs.get('buyers_order_number', None),
        'reference_field_1': kwargs.get('reference_field_1', None),
        'reference_field_2': kwargs.get('reference_field_2', None),
        'invoice_number': kwargs.get('invoice_number', None),
        'invoice_date': kwargs.get('invoice_date', None),
        'due_date': kwargs.get('due_date', None),
        'ocr_number': kwargs.get('ocr_number', None),
        'period':  invoice_period,
        'receiver_name': kwargs.get('receiver_name', None),
        'receiver_address': kwargs.get('receiver_address', None),
        'receiver_extra_fields': kwargs.get('receiver_extra_fields', []),
        'logo_path': logo_path,
        'company_name': kwargs.get('company_name', None),
        'company_address': kwargs.get('company_street_address', None),
        'company_number': kwargs.get('company_number', None),
        'company_vat_number': kwargs.get('company_vat_number', None),
        'company_website': kwargs.get('company_website', None),
        'company_phone': kwargs.get('company_phone', None),
        'extra_fields': kwargs.get('extra_fields', []),
        'invoice_header': kwargs.get('invoice_header', None),
        # below fields will be initialized to None since they should only be included on last page
        'footer_header_1': None,
        'footer_header_2': None,
        'footer_value_1': None,
        'footer_value_2': None,
        'total': None,
        'discount': None,
        'total_excluding_vat': None,
        'vat_amount': None,
        'payment_methods': []
    }
 
            
    # Get the total number of invoice rows
    total_rows = len(rows)

    # Calculate the number of pages required
    if total_rows <= rows_last_page:
        num_pages = 1
    else:
        num_pages = math.ceil((total_rows - rows_last_page) / rows_per_page) + 1

    # Initialize PdfMerger
    merger = PdfMerger()

    for page in range(num_pages):
        # Determine the rows for this page
        if page < num_pages - 1:  # Not the last page
            start_row = page * rows_per_page
            end_row = start_row + rows_per_page
            rows_this_page = rows[start_row:end_row]

        else:  # Last page
            start_row = page * rows_per_page
            end_row = start_row + rows_last_page
            rows_this_page = rows[start_row:end_row]
            # data to only include on last page
            context.update({
                'footer_header_1': kwargs.get('footer_header_1', None),
                'footer_header_2': kwargs.get('footer_header_2', None),
                'footer_value_1': kwargs.get('footer_value_1', None),
                'footer_value_2': kwargs.get('footer_value_2', None),
                'terms_of_payment': kwargs.get('terms_of_payment', None),
                'late_interest_rate': kwargs.get('late_interest_rate', None),
                'total_section': {
                    'total': kwargs.get('invoice_total', None),
                    'discount': kwargs.get('invoice_discount', None),
                    'total_excluding_vat': kwargs.get('invoice_total_excluding_vat', None),
                    'vat_amount': kwargs.get('invoice_total') - kwargs.get('invoice_total_excluding_vat'),
                },
                'payment_methods': kwargs.get('payment_methods', []),
            })
        
        context.update({
            'rows': rows_this_page,
            "page_number": page + 1,
            "total_pages": num_pages,
        })

        # Render the HTML with the rows for this page
        rendered = pdf_invoice_template.render(context)
        pdf = pdfkit.from_string(rendered, False)
        pdf_io = BytesIO(pdf)
        pdf_io.seek(0)

        # Append the PDF to the merger
        merger.append(pdf_io)

    
    # Write the merged PDF to a BytesIO object
    output_pdf_io = BytesIO()
    merger.write(output_pdf_io)
    output_pdf_io.seek(0)
    merger.close()

    # Create a Django ContentFile object
    pdf_file = ContentFile(output_pdf_io.read(), name=f'{invoice.invoice_number}.pdf')

    return pdf_file