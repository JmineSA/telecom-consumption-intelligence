FROM python:3.9-slim

WORKDIR /app

# Install system dependencies
RUN apt-get update && apt-get install -y \
    gcc \
    g++ \
    && rm -rf /var/lib/apt/lists/*

# Copy requirements
COPY requirements_modular.txt .
RUN pip install --no-cache-dir -r requirements_modular.txt

# Copy application
COPY . .

# Create directories
RUN mkdir -p logs reports

# Expose port
EXPOSE 8501

# Run streamlit
CMD ["streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]