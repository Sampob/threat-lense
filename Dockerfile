FROM python:3.12-slim

# Set the working directory in the container
WORKDIR /app

# Copy the current directory contents into the container
COPY . .

# Install dependencies
RUN pip install -r app/requirements.txt

# Expose the port that Flask runs on
EXPOSE 5000

# Define the command to run Flask
CMD ["flask", "run", "--host=0.0.0.0"]