# Use a lightweight Python Linux image
FROM python:3.10-slim

# Set the working directory inside the container
WORKDIR /app

# Install the GNU C++ multi-threading library required for LightGBM on Linux
RUN apt-get update && \
    apt-get install -y libgomp1 && \
    rm -rf /var/lib/apt/lists/*

# Copy your requirements and install them
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy the rest of your Aura AI code
COPY . .

# Tell LangChain to look for Ollama on the host Mac, not inside the container
ENV OLLAMA_HOST="http://host.docker.internal:11434"

# Expose Streamlit's default port
EXPOSE 8501

# Command to run the application
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0"]
