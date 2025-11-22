FROM python:3.11-slim

WORKDIR /app

# Install dependencies
RUN pip install --no-cache-dir \
    jupyter \
    notebook \
    matplotlib \
    numpy \
    ipywidgets

# Copy all files
COPY . /app

# Make start script executable
RUN chmod +x /app/start.sh

# Expose ports: 8888 for Jupyter, 8000 for HTML game
EXPOSE 8888 8000

CMD ["/bin/bash", "/app/start.sh"]
