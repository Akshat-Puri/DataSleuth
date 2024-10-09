from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required  # Import login_required
from django.contrib.auth import authenticate, login
from .models import Agent, File, Log  # Import the Log model for logging actions
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

        # Validate file size (Optional step to prevent large files)
        if uploaded_file.size > 10 * 1024 * 1024:  # Example: 10MB limit
            return render(request, 'upload.html', {'error': 'File too large (max 10MB allowed).'})

        # Process the file for each agent
        processed_files = []  # List to keep track of processed files (each entry is a tuple of (agent, file))

        try:
            for agent in agents:
                agent_id = agent.id

                # Determine file type and apply the appropriate processor
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

                processed_files.append((agent, processed_file))  # Add agent and processed file as tuple

                # Save the processed file details in the database for each agent
                with transaction.atomic():
                    new_file = File.objects.create(
                        agent=agent,
                        file_name=processed_file.split('/')[-1],
                        file_type=uploaded_file.name.split('.')[-1],
                        version_id=uuid.uuid4()  # Generate a new UUID for version control
                    )

                    # Log the file upload action for each agent
                    Log.objects.create(
                        agent=agent,
                        user=request.user if request.user.is_authenticated else None,
                        action='UPLOAD',
                        description=f'File {new_file.file_name} uploaded and processed for agent {agent.name}.'
                    )

        except Exception as e:
            logger.error(f'Error processing file: {e}')
            return render(request, 'upload.html', {'error': f'Error processing file: {str(e)}'})

        # Render the success page with the processed files
        return render(request, 'file_success.html', {'processed_files': processed_files})

    # If GET, render the upload page with a list of agents
    agents = Agent.objects.all()
    return render(request, 'upload.html', {'agents': agents})


@login_required  # Use the login_required decorator to restrict access to the log list
def log_list(request):
    logs = Log.objects.all().order_by('-timestamp')
    return render(request, 'log_list.html', {'logs': logs})


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('log_list')  # Redirect to logs page
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials.'})

    return render(request, 'login.html')


# Success page after file upload
def file_success(request):
    return render(request, 'file_success.html')
