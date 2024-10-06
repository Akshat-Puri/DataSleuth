import PyPDF2


def check_metadata(file_path):
    pdf_reader = PyPDF2.PdfReader(file_path)
    metadata = pdf_reader.metadata
    print(metadata)


check_metadata('Test2_2.pdf')
