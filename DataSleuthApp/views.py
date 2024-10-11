from django.shortcuts import render, redirect, get_object_or_404
from django.core.files.storage import FileSystemStorage
from django.http import HttpResponse, JsonResponse
from django.db import transaction
from django.contrib.auth.decorators import login_required  # Import login_required
from django.contrib.auth.hashers import check_password
from django.contrib.auth import authenticate, login, logout, get_user_model
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
@login_required  # Use the login_required decorator to restrict the upload of file.
def upload_file(request):
    if request.method == 'POST':

        # Decode JSON list of agent IDs
        agent_ids = json.loads(request.POST.get('agent_ids', '[]'))
        # Get the uploaded file from the request
        uploaded_file = request.FILES.get('file')
        # Ensure agent IDs and file are provided
        if not agent_ids or not uploaded_file:
            return render(request, 'upload.html', {'error': 'At least one Agent and file are required!'})
        # Validate file size (Optional step to prevent large files)
        max_file_size = 10 * 1024 * 1024  # Example: 10MB limit
        if uploaded_file.size > max_file_size:
            return render(request, 'upload.html', {'error': 'File too large. Maximum allowed size is 10MB.'})
        # Ensure agents exist by their IDs (IDs are integers)
        agents = Agent.objects.filter(id__in=agent_ids)
        if not agents.exists():
            return render(request, 'upload.html', {'error': 'Selected agents not found!'})

        # Save the uploaded file
        fs = FileSystemStorage()
        file_name = fs.save(uploaded_file.name, uploaded_file)
        file_path = fs.path(file_name)
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

            # After creating logs, clean up old logs if they exceed the limit
            clean_up_old_logs()

        except Exception as e:
            logger.error(f'Error processing file: {e}')
            return render(request, 'upload.html', {'error': f'Error processing file: {str(e)}'})
        # Render the success page with the processed files
        return render(request, 'file_success.html', {'processed_files': processed_files})

    # If GET, render the upload page with a list of agents
    agents = Agent.objects.all()
    return render(request, 'upload.html', {'agents': agents})


def logging(request):
    # Logic to show logs
    logs = Log.objects.all().order_by('-timestamp')
    return render(request, 'logging.html', {'logs': logs})


# View to delete logs
def delete_logs(request):
    if request.method == "POST":
        # Get the superuser password from the request body
        data = json.loads(request.body)
        password = data.get('password', '')

        # Verify if the provided password matches the superuser's password
        User = get_user_model()
        superuser = User.objects.get(is_superuser=True)  # Get the superuser
        if check_password(password, superuser.password):
            # Logic to delete logs
            Log.objects.all().delete()  # Example delete operation
            return JsonResponse({
                "success": True
            })

        return JsonResponse({"success": False, "message": "Invalid superuser password."})


# Function to clean up old logs if they exceed the limit of 50
def clean_up_old_logs():
    max_logs = 50
    total_logs = Log.objects.count()  # Get total count of logs

    if total_logs > max_logs:
        logs_to_delete = total_logs - max_logs
        # Delete the oldest logs based on timestamp
        Log.objects.order_by('timestamp')[:logs_to_delete].delete()


def custom_login_view(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')
        user = authenticate(request, username=username, password=password)

        if user is not None:
            login(request, user)
            return redirect('upload_file')  # Redirect to logs page
        else:
            return render(request, 'login.html', {'error': 'Invalid credentials.'})

    return render(request, 'login.html')


# Custom logout and stop server
def custom_logout(request):
    logout(request)  # Logout the user
    return redirect('home')  # Redirect to the home page


# Success page after file upload
def file_success(request):
    return render(request, 'file_success.html')


'''
Issues and Improvements:
1) upload_file View:
    i) File Size Validation: 
        The file size check is done after saving the file to the file system. This could lead to performance issues or 
        disk space problems if large files are uploaded. You should validate the file size before saving it. --Done
    ii) File Path Security: 
        Make sure you're not exposing raw file paths to users. Django’s FileSystemStorage is secure, but be cautious when 
        dealing with file paths.
    iii) File Overwriting: 
        If a file with the same name exists, Django’s default FileSystemStorage will rename the file. If you want to 
        explicitly prevent overwriting, handle this in the FileSystemStorage. -- Done
    iv) File Process Exception Handling: 
        You handle exceptions well, but it would be helpful to provide more specific error messages to the user instead 
        of a generic message like Error processing file. -- Done
    v) Transaction Handling: 
        Good use of transaction.atomic(), but make sure you’re handling the case where the database rollback happens 
        (such as if file creation fails).
        
2) delete_logs View: --Done
    i) Hardcoded Superuser Username: 
        The superuser username is hardcoded ('your_superuser_username'). This is not a good practice. You should either 
        dynamically fetch the superuser or allow flexibility in choosing the user. Additionally, it’s better to avoid 
        exposing this username in the codebase. -- Done
    ii) Security with Password Handling: 
        It's good that you're using Django’s authenticate() function, but ensure the request is made over HTTPS when 
        handling sensitive information like passwords. -- Done (will do in production)
        
3) Logout and Server Stop Logic: -- Done (avoided but can be done on production)
    i) Killing the Server: 
        Using os.system('taskkill /f /im python.exe') is very specific to a Windows environment. This approach is risky 
        in a production setting. It's advisable not to put any logic related to killing the process in a Django view, 
        especially for cross-platform development. In a production environment, you would handle server restarts and 
        shutdowns with more robust tools (like systemctl or using a web server like Nginx/Apache). -- Done (avoided)
    ii) Better Approach for Development Environment: 
        For a dev environment, you could show a message informing the user to stop the server manually instead of directly 
        killing it. This way, you avoid hard-to-debug errors if something goes wrong. -- Done (avoided)

4) File Type Handling:
    You are checking for specific file extensions, but it might be helpful to handle other cases like .jpeg and .png for image processing.
    Consider centralizing file type handling into a utility function to make it easier to add new file types in the future.

5) Login and Logout Views: -- Done (can be done before production, not necessary on development but can be tested)
    The login_required decorator for logging is a good addition.
    The custom login and logout views seem fine. However, for security purposes, make sure to limit login attempts to 
    prevent brute-force attacks (you could integrate something like django-axes). 

6) Logging:
    You are using Django’s built-in logging, which is great. However, you might want to ensure that logs also capture IP 
    addresses, especially for admin-related actions like delete_logs. You can do that by including request.META.get('REMOTE_ADDR') 
    in the log message for more traceability.

7) Success Page Redirect:
    After the file is successfully processed and logged, it's good practice to redirect the user to the success page with 
    some sort of feedback message instead of just rendering it.

8) CSRF Protection:
    Ensure that CSRF protection is enabled by default, especially in views like delete_logs where POST actions occur.
'''