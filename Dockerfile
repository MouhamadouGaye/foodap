# Use Amazon Linux 2023 as the base image
FROM amazonlinux:2023

# Install Python 3.11 and pip
RUN yum update -y && \
    yum install -y python3.11 python3.11-pip && \
    yum install -y gcc gcc-c++ make libpq-devel

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# Upgrade pip to the latest version
RUN python3.11 -m pip install --upgrade pip

# Install the dependencies from the requirements file
RUN python3.11 -m pip install --no-cache-dir -r requirements.txt

# Expose port 8000 (the port you want to run FastAPI on)
EXPOSE 8000

# Command to run the FastAPI app with Uvicorn
CMD ["python3.11", "-m", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]




