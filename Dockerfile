FROM python:3.11-slim

WORKDIR /app

# Install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application files
COPY live_paper_trade_v5.py .
COPY api_server.py .
COPY live_state.json .

# Expose port for API
EXPOSE 8000

# Create startup script
RUN echo '#!/bin/bash\n\
python live_paper_trade_v5.py & \n\
uvicorn api_server:app --host 0.0.0.0 --port 8000\n\
' > /app/start.sh && chmod +x /app/start.sh

CMD ["/app/start.sh"]
 
