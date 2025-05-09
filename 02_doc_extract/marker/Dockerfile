# Use an official Python runtime as a parent image
FROM python:3.10

# Set the working directory in the container
WORKDIR /usr/src/app

# Clone the repository
RUN git clone https://github.com/VikParuchuri/marker.git
WORKDIR /usr/src/app/marker

# Install system requirements
# Note: Scripted installation of tesseract and ghostscript may need adjustments
RUN apt-get update && \
    apt-get install -y $(cat scripts/install/apt-requirements.txt)

# Install Tesseract
RUN apt-get update && \
    apt-get install -y lsb-release apt-transport-https wget && \
    wget -qO - https://notesalexp.org/debian/alexp_key.asc | apt-key add - && \
    echo "deb https://notesalexp.org/tesseract-ocr5/$(lsb_release -cs)/ $(lsb_release -cs) main" \
    | tee /etc/apt/sources.list.d/notesalexp.list > /dev/null && \
    apt-get update -oAcquire::AllowInsecureRepositories=true && \
    apt-get install -y notesalexp-keyring --allow-unauthenticated && \
    apt-get update && \
    apt-get install -y tesseract-ocr && \
    rm -rf /var/lib/apt/lists/*

# Install ffmpeg and libsm6 libxext6
RUN apt-get update && apt-get install ffmpeg libsm6 libxext6 -y

# Install Ghostscript
RUN wget https://github.com/ArtifexSoftware/ghostpdl-downloads/releases/download/gs10012/ghostscript-10.01.2.tar.gz && \
    tar -xvf ghostscript-10.01.2.tar.gz && \
    cd ghostscript-10.01.2 && \
    ./configure && \
    make install && \
    cd .. && \
    rm -rf ghostscript-10.01.2 ghostscript-10.01.2.tar.gz

# Find the tessdata directory and create a local.env file with the TESSDATA_PREFIX
RUN tessdata_path=$(find / -name tessdata -print -quit) && \
    echo "TESSDATA_PREFIX=${tessdata_path}" > local.env

# Install Python dependencies
RUN pip install poetry
RUN poetry install

# Update PyTorch (will be configured at runtime based on GPU/CPU selection)
RUN pip install --upgrade pip
# PyTorch installation will be handled by the run script
RUN pip install --no-cache-dir --no-warn-script-location PyMuPDF pydantic ftfy python-dotenv \ 
    pydantic-settings tabulate pyspellchecker ocrmypdf nltk thefuzz scikit-learn texify \
    python-magic bs4 tabled-pdf markdownify streamlit

COPY . .

RUN python convert_single.py --output_dir test_output --output_format markdown

# Install API server dependencies
RUN pip install -U uvicorn fastapi python-multipart

# The command to run the application
CMD ["poetry", "run", "marker_server", "--port", "2080"]

