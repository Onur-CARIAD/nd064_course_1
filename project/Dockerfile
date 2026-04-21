FROM python:3.8-slim

WORKDIR /app

# Copy requirements from techtrends subfolder
COPY techtrends/requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY techtrends/ .

# Initialize the database
RUN python init_db.py

EXPOSE 3111

CMD ["python", "app.py"]