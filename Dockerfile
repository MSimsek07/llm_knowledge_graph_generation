# Use a base image
FROM python:3.11.8

# Set working directory
WORKDIR /app

# Copy requirements.txt
COPY requirements.txt .

# Install dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of the application
COPY . .

# Set environment variables
ENV OPENAI_API_KEY ""
ENV LANGCHAIN_API_KEY ""
ENV SERP_API_KEY ""

# Expose the port your app runs on
EXPOSE 8000

# Command to run the application
CMD ["uvicorn", "backend2:app", "--host", "0.0.0.0", "--port", "8000"]
