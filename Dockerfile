
FROM python:3.10-slim  # Adjust based on compatibility


# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Install system dependencies (if needed)
RUN apt-get update && apt-get install -y libpq-dev build-essential

# Upgrade pip to the latest version
RUN pip install --upgrade pip

# Install the dependencies from the requirements file
RUN pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (the port you want to run FastAPI on)
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]



