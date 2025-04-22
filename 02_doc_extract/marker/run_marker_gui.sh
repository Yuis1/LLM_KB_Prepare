#!/bin/bash

echo "=== Marker PDF GUI Server Setup ==="
echo "Please select the processing mode:"
echo "1) GPU (CUDA) - Faster processing with GPU support"
echo "2) CPU - Compatible with all systems"

read -p "Enter your choice (1 or 2): " choice

# Build the Docker image
echo "Building Docker image..."
docker build -t marker-pdf-gui .

# Run the container based on user's choice
if [ "$choice" == "1" ]; then
    echo "Starting Marker PDF GUI with GPU support..."
    # Install PyTorch with CUDA support inside the container
    docker run -it --rm \
        --gpus all \
        -e TORCH_INSTALL="pip install torch torchvision torchaudio" \
        -p 2080:2080 \
        -v "$(pwd)/data:/usr/src/app/data" \
        marker-pdf-gui
else
    echo "Starting Marker PDF GUI with CPU support..."
    # Install PyTorch CPU version inside the container
    docker run -it --rm \
        -e TORCH_INSTALL="pip install torch torchvision torchaudio --index-url https://download.pytorch.org/whl/cpu" \
        -p 2080:2080 \
        -v "$(pwd)/data:/usr/src/app/data" \
        marker-pdf-gui
fi

echo "Marker PDF GUI server is running at http://localhost:2080"
echo "You can access the API documentation at http://localhost:2080/docs"