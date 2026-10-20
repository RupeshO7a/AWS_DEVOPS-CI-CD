# 1. Start from a small official image that already contains Python 3.12
FROM python:3.12-slim
 
# 2. Python settings: no .pyc files, show logs immediately
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1
 
# 3. Work inside the /app folder in the container
WORKDIR /app
 
# 4. Install the libraries first (Docker caches this step to build faster)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
 
# 5. Copy the rest of our code into the image
COPY . .
 
# 6. The app listens on port 8000
EXPOSE 8000
 
# 7. The command that starts the app when the container starts
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
