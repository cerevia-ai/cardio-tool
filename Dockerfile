FROM python:3.10-slim

WORKDIR /app

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

# Set Streamlit environment variable for headless mode
ENV STREAMLIT_BROWSER_GATHER_USAGE_STATS=false

EXPOSE 8080

# Run Streamlit app using App Runner's dynamic port
CMD ["sh", "-c", "streamlit run cardio_app.py --server.port=$PORT --server.address=0.0.0.0"]
