# Dockerfile
FROM python:3.11.9-slim

# Set working directory
WORKDIR /app

# Copy only requirements first (for better layer caching)
COPY requirements.txt .

# Upgrade pip and install dependencies
RUN pip install --upgrade pip setuptools wheel \
    && pip install -r requirements.txt

# Copy the rest of your code
COPY . .

# Expose whatever port your FastAPI app listens on
EXPOSE 8000

# Command to run your app
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
