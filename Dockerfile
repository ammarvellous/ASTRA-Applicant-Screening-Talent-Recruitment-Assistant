FROM python:3.12-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    build-essential \
    curl \
    && rm -rf /var/lib/apt/lists/*

# Install Rust compiler (needed for tiktoken)
RUN curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs | sh -s -- -y
ENV PATH="/root/.cargo/bin:${PATH}"

# Copy requirements and install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Optional: Install PDF and DOCX parsing libraries
RUN pip install --no-cache-dir PyPDF2 python-docx

# Copy application code
COPY . .

# Expose Streamlit port
EXPOSE 8501

# Environment variables (these will need to be set when running the container)
# MONGODB_URI, GEMINI_API_KEY, WATSONX_APIKEY, WATSONX_PROJECT_ID, WATSONX_URL

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]