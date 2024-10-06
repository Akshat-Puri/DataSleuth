from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.db import transaction
from .models import Agent, File
from .preprocessing.text_preprocessor import preprocess_text
from .preprocessing.pdf_preprocessor import preprocess_pdf
from .preprocessing.image_preprocessor import preprocess_image
import uuid
import logging

logger = logging.getLogger(__name__)  # Set up logging


def home(request):
    return render(request, 'home.html')


# View for file upload
def upload_file(request):
    if request.method == 'POST':
        agent_id = request.POST.get('agent_id')
        uploaded_file = request.FILES.get('file')

        # Ensure agent ID and file are provided
        if not agent_id or not uploaded_file:
            return render(request, 'upload.html', {'error': 'Agent ID and file are required!'})

        # Check if the agent exists
        try:
            agent = Agent.objects.get(id=agent_id)
        except Agent.DoesNotExist:
            return render(request, 'upload.html', {'error': 'Agent not found!'})

        # Save the uploaded file
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_name)

        # Process the file based on its type
        try:
            processed_file = None
            if uploaded_file.name.endswith('.txt'):
                processed_file = preprocess_text(file_path, agent_id)
            elif uploaded_file.name.endswith('.pdf'):
                processed_file = preprocess_pdf(file_path, agent_id)
            elif uploaded_file.name.endswith('.jpg') or uploaded_file.name.endswith('.bmp'):
                processed_file = preprocess_image(file_path, agent_id)
            else:
                return render(request, 'upload.html', {'error': 'Unsupported file type'})

            if processed_file is None:
                raise Exception('File processing failed')

        except Exception as e:
            logger.error(f'Error processing file: {e}')
            return render(request, 'upload.html', {'error': f'Error processing file: {str(e)}'})

        # Save the processed file details in the database
        try:
            with transaction.atomic():
                File.objects.create(
                    agent=agent,
                    file_name=processed_file.split('/')[-1],
                    file_type=uploaded_file.name.split('.')[-1],
                    version_id=uuid.uuid4()  # Generate a new UUID for version control
                )
        except Exception as e:
            logger.error(f'Error saving file record: {e}')
            return render(request, 'upload.html', {'error': 'Error saving file record'})

        return redirect('file_success')

    # If GET, render the upload page with a list of agents
    agents = Agent.objects.all()
    return render(request, 'upload.html', {'agents': agents})


# Success page after file upload
def file_success(request):
    return render(request, 'file_success.html')


'''
1) Error Logging:
    Added logging to capture and log any issues in processing or saving files. This makes it easier to debug and monitor 
    the system.

2) Transaction Handling:
    The with transaction.atomic() block ensures that the database operations (like saving the File object) happen 
    atomically, meaning that if something goes wrong, it will not leave partial changes in the database.

3) Better Error Handling:
    Enhanced error handling to log and return informative error messages if something goes wrong during file processing 
    or saving the file record.

4) File Type Handling:
    The processed_file is initialized to None, and an additional check ensures that file processing didn't silently fail.
'''


'''
Additional Recommendations:
1) Validation for File Size:
    You may want to add file size validation to prevent the upload of excessively large files.

2) Testing:
    Be sure to test the view for various file types (.txt, .pdf, .jpg, .bmp) to ensure everything works as expected.
    Test edge cases like missing or invalid agent IDs.

3) Form Improvements:
    Consider adding client-side validation in the HTML forms for selecting agents and uploading files to improve user 
    experience.
'''
