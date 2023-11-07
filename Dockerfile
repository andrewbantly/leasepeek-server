# Use an official Python runtime as a parent image
FROM python:3.11-bookworm

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
