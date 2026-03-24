# Python image to use.
FROM python:3.10

# Expose 8080 as the port
EXPOSE 8080

# Set the working directory to /app
WORKDIR /app

# 1. Copy ONLY requirements first to use Docker caching
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 2. Copy the rest of the code (this happens fast)
COPY . .

# The main command to run when the container starts.
ENTRYPOINT ["streamlit", "run", "app.py", "--server.port=8080", "--server.address=0.0.0.0"]