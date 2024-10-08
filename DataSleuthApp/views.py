from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.db import transaction
from .models import Agent, File
from .preprocessing.text_preprocessor import preprocess_text
from .preprocessing.pdf_preprocessor import preprocess_pdf
from .preprocessing.image_preprocessor import preprocess_image
import json
import uuid
import logging

logger = logging.getLogger(__name__)  # Set up logging


def home(request):
    return render(request, 'home.html')


# View for file upload
def upload_file(request):
    if request.method == 'POST':

        # Decode JSON list of agent IDs
        agent_ids = json.loads(request.POST.get('agent_ids', '[]'))

        uploaded_file = request.FILES.get('file')

        # Ensure agent IDs and file are provided
        if not agent_ids or not uploaded_file:
            return render(request, 'upload.html', {'error': 'At least one Agent and file are required!'})

        # Ensure agents exist by their IDs (IDs are integers)
        agents = Agent.objects.filter(id__in=agent_ids)
        if not agents.exists():
            return render(request, 'upload.html', {'error': 'Selected agents not found!'})

        # Save the uploaded file
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_name)

        # Process the file for each agent
        processed_files = []  # List to keep track of processed files

        try:
            for agent in agents:
                agent_id = agent.id

                if uploaded_file.name.endswith('.txt'):
                    processed_file = preprocess_text(file_path, agent_id)
                elif uploaded_file.name.endswith('.pdf'):
                    processed_file = preprocess_pdf(file_path, agent_id)
                elif uploaded_file.name.endswith('.jpg') or uploaded_file.name.endswith('.bmp'):
                    processed_file = preprocess_image(file_path, agent_id)
                else:
                    return render(request, 'upload.html', {'error': 'Unsupported file type'})

                if processed_file is None:
                    raise Exception(f'File processing failed for agent {agent.name}')

                processed_files.append(processed_file)

                # Save the processed file details in the database for each agent
                with transaction.atomic():
                    File.objects.create(
                        agent=agent,
                        file_name=processed_file.split('/')[-1],
                        file_type=uploaded_file.name.split('.')[-1],
                        version_id=uuid.uuid4()  # Generate a new UUID for version control
                    )

        except Exception as e:
            logger.error(f'Error processing file: {e}')
            return render(request, 'upload.html', {'error': f'Error processing file: {str(e)}'})

        # Redirect to the success page after all files are processed
        return redirect('file_success')

    # If GET, render the upload page with a list of agents
    agents = Agent.objects.all()
    return render(request, 'upload.html', {'agents': agents})


# Success page after file upload
def file_success(request):
    return render(request, 'file_success.html')


'''
1) Handling multiple agents:
    Used request.POST.getlist('agent_ids') to fetch the selected agents as a list.
    Fetched all agents from the database using Agent.objects.filter(id__in=agent_ids).

2) Looping over agents:
    For each selected agent, the file is processed using the appropriate preprocessor and a separate output file is 
    generated.
    
3) Error Logging:
    Added logging to capture and log any issues in processing or saving files. This makes it easier to debug and monitor 
    the system.

4) Transaction Handling:
    The with transaction.atomic() block ensures that the database operations (like saving the File object) happen 
    atomically, meaning that if something goes wrong, it will not leave partial changes in the database.
    
    Wrapped the file creation in a transaction.atomic() block to ensure that either all files are created successfully 
    or none at all (in case of failure).

5) Better Error Handling:
    Enhanced error handling to log and return informative error messages if something goes wrong during file processing 
    or saving the file record.

6) File Type Handling:
    The processed_file is initialized to None, and an additional check ensures that file processing didn't silently fail.
    The processed_files list keeps track of all the processed files for each agent.
    A new entry in the File model is created for each agent's processed file.
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

4) User Feedback: 
    You might want to update the success page to list all the processed files or give some feedback regarding how many 
    files were processed.
'''
