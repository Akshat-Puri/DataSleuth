import PyPDF2
import os

'''PDF File Preprocessing: -
Modifying the metadata or embed invisible text using PyPDF2'''


def preprocess_pdf(file_path, agent_id):
    try:
        # Open the PDF file
        pdf_reader = PyPDF2.PdfReader(file_path)
        pdf_writer = PyPDF2.PdfWriter()

        # Add all pages to the new PDF
        for page_num in range(len(pdf_reader.pages)):
            page = pdf_reader.pages[page_num]
            pdf_writer.add_page(page)

        # Add agent information to PDF metadata
        metadata = pdf_reader.metadata or {}
        metadata.update({
            '/AgentID': agent_id,
            '/ModifiedBy': 'DataLeakageDetection'
        })
        pdf_writer.add_metadata(metadata)

        # Generate output file name
        output_file = f"{os.path.splitext(file_path)[0]}_{agent_id}.pdf"

        # Write the new PDF to disk
        with open(output_file, 'wb') as file:
            pdf_writer.write(file)

        return output_file  # Return the path to the processed PDF file

    except Exception as e:
        # Log or print the error (for debugging purposes)
        print(f"Error processing PDF file {file_path}: {e}")
        return None


'''
1) try-except Block:
    This ensures that if something goes wrong (like an invalid file, I/O errors, etc.), the exception is caught, and an 
    error message is printed or logged.

2) Safe Metadata Handling:
    Before updating the metadata, it checks if any metadata exists in the original PDF. This prevents overwriting or 
    missing important fields. If no metadata is found, it initializes an empty dictionary.

3) File Path Handling:
    The os.path.splitext(file_path)[0] safely handles file names without extensions, making the code more robust when 
    dealing with different file paths.

4) Return Value:
    In case of failure (e.g., if an exception is raised), the function returns None to signal that the preprocessing was 
    unsuccessful.
'''


'''
Additional Improvements that can be done:
1) Agent-specific Watermarks:
    We could consider adding agent-specific watermarks directly on the pages as an additional measure of traceability, 
    especially if metadata tampering is a concern.

2) Large Files Handling:
    For very large PDFs, we might want to process the file in chunks or add memory management techniques if the file 
    size exceeds typical limits.
'''


'''
To check the metadata of the processed pdf: -

import PyPDF2

def check_metadata(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    metadata = pdf_reader.metadata
    print(metadata)

check_metadata('Test2_2.pdf')
'''