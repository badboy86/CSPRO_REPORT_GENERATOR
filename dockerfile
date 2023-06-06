# Base image
FROM python:3.9-slim-buster

# Set working directory
WORKDIR /app

# Copy requirements.txt to the container
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the application code to the container
COPY . .

# Expose the port your Flask app will run on
EXPOSE 5000

# Define the command to run your Flask app
CMD ["python", "app.py"]
