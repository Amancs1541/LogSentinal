import os
from werkzeug.utils import secure_filename

ALLOWED_EXTENSIONS = {"log", "txt"}

def allowed_file(filename):
    return "." in filename and filename.rsplit(".", 1)[1].lower() in ALLOWED_EXTENSIONS

def save_uploaded_file(file, upload_folder):
    if not allowed_file(file.filename):
        raise ValueError("Unsupported file type")
    filename = secure_filename(file.filename)
    filepath = os.path.join(upload_folder, filename)
    file.save(filepath)
    return filepath, filename
