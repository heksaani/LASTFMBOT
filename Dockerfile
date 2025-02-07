# Use a Python 3 base image
FROM python:3.11-slim

# Set the working directory inside the container
WORKDIR /app

# Copy the entire project directory into the container
COPY . .

# Install the dependencies from requirements.txt
RUN pip install --no-cache-dir -r requirements.txt

# Set the entry point to run the bot (or your main application)
CMD ["python", "main.py"]
