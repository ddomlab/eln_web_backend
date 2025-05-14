FROM continuumio/miniconda3:latest

# Set working directory
WORKDIR /app

# Copy everything
COPY . .

# Create conda environment from environment.yml
COPY environment.yml .
RUN conda env create -f environment.yml

# Activate the environment
SHELL ["conda", "run", "-n", "customenv", "/bin/bash", "-c"]

# Optional: install Flask app if it's a package
# RUN conda run -n customenv pip install -e .

# Expose Flask port
EXPOSE 5000

# Run Flask app using the conda env
CMD ["conda", "run", "-n", "customenv", "python", "app.py"]
