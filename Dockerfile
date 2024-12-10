# Use an official Python runtime as a parent image
FROM python:3.11-slim

# Install necessary tools
RUN apt-get update && apt-get install -y \
    wget \
    curl \
    git

# Set the working directory in the container
WORKDIR /webapp

# Download GitHub CLI
RUN curl -fsSL https://cli.github.com/packages/githubcli-archive-keyring.gpg | dd of=/usr/share/keyrings/githubcli-archive-keyring.gpg \
    && chmod go+r /usr/share/keyrings/githubcli-archive-keyring.gpg \
    && echo "deb [arch=$(dpkg --print-architecture) signed-by=/usr/share/keyrings/githubcli-archive-keyring.gpg] https://cli.github.com/packages stable main" | tee /etc/apt/sources.list.d/github-cli.list > /dev/null \
    && apt-get update \
    && apt-get install -y gh

# Install project dependencies
COPY requirements.txt /webapp/
RUN pip install --no-cache-dir -r requirements.txt

# Copy the current directory contents into the container
COPY . /webapp/

# Download model from GitHub Release
ARG GITHUB_TOKEN
ARG REPO_OWNER
ARG REPO_NAME
RUN mkdir -p /webapp/models/rfcn/1 \
    && cd /webapp/models/rfcn/1 \
    && gh release download v1.0 \
       --repo ${REPO_OWNER}/${REPO_NAME} \
       --pattern "saved_model.pb" \
    || echo "Model download failed"

# Expose port for the Flask application
EXPOSE 8085

# Run the application
CMD ["python", "-m", "counter.entrypoints.webapp"]