FROM python:3.12-slim

# Set working directory
WORKDIR /app

# Copy everything
COPY . .
COPY eln_packages_common ./eln_packages_common

# Create conda environment from environment.yml
# COPY environment.yml .
# RUN conda env create -f environment.yml
RUN pip install ./eln_packages_common --no-cache-dir
RUN pip install --no-cache-dir -r requirements.txt
RUN pip install --no-cache-dir gunicorn

# Activate the environment
SHELL ["conda", "run", "-n", "customenv", "/bin/bash", "-c"]

# Optional: install Flask app if it's a package
# RUN conda run -n customenv pip install -e .

# Expose Flask port
EXPOSE 5000

# Run Flask app
CMD ["gunicorn", "-w", "4", "-b", "0.0.0.0:5000", "app:app"]

