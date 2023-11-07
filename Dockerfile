# Use an official Python runtime as a parent image
FROM python:3.11-bookworm

# Set environment variable PYTHONUNBUFFERED to a non-empty value, ensuring that the Python output is sent straight to terminal (e.g. your container log) without being first buffered and that you can see the output of your application (e.g. Django logs) in real time.
ENV PYTHONUNBUFFERED 1

# Set environment variable PYTHONDONTWRITEBYTECODE to a non-empty value (typically "1") to prevent Python from writing .pyc files to disk (equivalent to python -B option).
ENV PYTHONDONTWRITEBYTECODE 1

# Expose port 8000 for the web server
EXPOSE 8000

# Set the working directory in the container to /app
WORKDIR /app

# Copy the requirements.txt file into the container at /app
COPY requirements.txt /app/

# Install any needed packages specified in requirements.txt
RUN pip3 install --no-cache-dir -r requirements.txt

# Copy the rest of the application into the container at /app
COPY . /app/

# Define the default command to run when starting the container
CMD ["python3", "manage.py", "runserver", "0.0.0.0:8000"]
