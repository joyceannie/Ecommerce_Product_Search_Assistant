# Use an official Python runtime as a parent image
FROM python:3.10-slim AS base

# Set the working directory
WORKDIR /app

# Copy the current directory contents into the container at /app
COPY . /app

# # Copy data to container at /data
# COPY data/cleaned_data.json data/cleaned_data.json

# Install any needed packages specified in requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# # Stage 2: Initialization stage
# FROM base AS init

# COPY create_index.py .

# CMD ["python", "create_index.py"]


# Make port 5000 available to the world outside this container
EXPOSE 5000

# # Define environment variable
ENV FLASK_APP=app.py
ENV FLASK_RUN_HOST=0.0.0.0

# Run the Flask application
CMD ["flask", "run", "--reload"]