#!/bin/bash
set -e  # Exit on error

INSTALL_PATH="${HOME}/projects/special_agent/"
if [ ! -d "$INSTALL_PATH" ]; then
    mkdir -p "$INSTALL_PATH"
fi

cd $INSTALL_PATH
echo "Installing to $INSTALL_PATH"

# Update system & install curl with retry
if ! command -v curl > /dev/null 2>&1; then
    echo "Installing curl..."
    sudo apt update || (echo "apt update failed—check internet/repos" && exit 1)
    sudo apt install -y curl || (echo "curl install failed" && exit 1)
fi

# Optional: Auto-install NVIDIA/CUDA if missing (uncomment if needed)
if ! command -v nvidia-smi > /dev/null 2>&1; then
    echo "NVIDIA missing—installing CUDA 12.6..."
    wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu2404/x86_64/cuda-keyring_1.1-1_all.deb
    sudo dpkg -i cuda-keyring_*.deb
    sudo apt update
    sudo apt install -y cuda-toolkit-12-6
    rm cuda-keyring_*.deb
    echo "Reboot required after install. Run 'export PATH=/usr/local/cuda-12.6/bin:\$PATH' then re-run script."
    exit 1
fi

# Install Ollama with retry
if ! command -v ollama > /dev/null 2>&1; then
    echo "Installing Ollama..."
    curl -fsSL https://ollama.com/install.sh | sh -s -- --verbose || {
        echo "Ollama install failed—retrying manual..."
        curl -L -o ollama-linux-amd64 https://github.com/ollama/ollama/releases/latest/download/ollama-linux-amd64
        sudo install ollama-linux-amd64 /usr/local/bin/ollama
        rm ollama-linux-amd64
    }
    sudo systemctl start ollama
    sudo usermod -aG video $USER  # GPU access
fi

# Pull model with VRAM check
MODEL="qwen2.5:14b-instruct-q6_K"
if ! ollama list | grep -q "$MODEL"; then
    echo "Pulling $MODEL (may take 30-60 min; ~40 GB download)..."
    echo gpu VRAM is $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits) MB
    OLLAMA_MAX_LOADED_MODELS=1 ollama pull "$MODEL" || {
        echo "Pull failed—trying smaller quant..."
        ollama pull qwen2.5:14b-instruct-q6_K
    }
fi

# Pull model with VRAM check
MODEL="llama3.2:3b"
if ! ollama list | grep -q "$MODEL"; then
    echo "Pulling $MODEL (may take 30-60 min; ~40 GB download)..."
    echo gpu VRAM is $(nvidia-smi --query-gpu=memory.total --format=csv,noheader,nounits) MB
    OLLAMA_MAX_LOADED_MODELS=1 ollama pull "$MODEL" || {
        echo "Pull failed"
        exit 1
    }
fi

# Python venv with upgraded pip
python -m venv venv
source venv/bin/activate
pip install --upgrade pip
pip install --no-warn-conflicts crewai langchain-ollama langchain-community chromadb watchdog python-dotenv chainlit pypdf python-docx pymupdf pillow imap-tools

# check installs
echo "Verifying python dependencies can be imported..."
for pkg in crewai langchain_ollama langchain_community chromadb watchdog python_dotenv chainlit pypdf python_docx pymupdf pillow imap_tools; do
    if [ "$pkg" == "langchain_ollama" ]; then
        pkg="langchain_ollama"  # Adjust for import name
    elif [ "$pkg" == "langchain_community" ]; then
        pkg="langchain_community"  # Adjust for import name
    elif [ "$pkg" == "python_dotenv" ]; then
        pkg="dotenv"  # Adjust for import name
    elif [ "$pkg" == "python_docx" ]; then
        pkg="docx"  # Adjust for import name
    elif [ "$pkg" == "pillow" ]; then
        pkg="PIL"  # Adjust for import name
    fi
    echo "checking $pkg install"
    python -c "import $pkg" || { echo "Package $pkg failed to import"; exit 1; }
done

echo checking imap_tools install
python -c "from imap_tools import MailBox; print('OK')"

echo "Setup complete! Run 'source venv/bin/activate && ollama serve' in one terminal, then test with 'ollama run $MODEL \"Hello world\"'."