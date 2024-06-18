from google.oauth2 import service_account
from googleapiclient.discovery import build
import pandas as pd
import csv

# Path to your service account key file
SERVICE_ACCOUNT_FILE = 'path/to/your/service_account.json'
# The folder ID from which to list the images
FOLDER_ID = '1DqwGcOzNphfdYdu-IjnARmySg6Bm1dQZ'

# Authenticate using the service account file
credentials = service_account.Credentials.from_service_account_file(SERVICE_ACCOUNT_FILE, scopes=["https://www.googleapis.com/auth/drive"])

# Initialize the Google Drive API client
service = build('drive', 'v3', credentials=credentials)

def list_files_in_folder(folder_id):
    query = f"'{folder_id}' in parents and mimeType='image/jpeg'"
    results = service.files().list(q=query, fields="files(id, name)").execute()
    return results.get('files', [])

def generate_direct_link(file_id):
    return f'https://drive.google.com/uc?export=view&id={file_id}'

# List files in the specified folder
files = list_files_in_folder(FOLDER_ID)

# Generate a list of direct links
file_links = [{'image_url': generate_direct_link(file['id'])} for file in files]

# Create a DataFrame
df = pd.DataFrame(file_links)

# Write to CSV
df.to_csv('images.csv', index=False)
