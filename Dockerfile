FROM python:3.12-slim

WORKDIR /app

# Copy everything first so uv can find the package source
COPY . .

# Install uv and dependencies
RUN pip install uv
RUN uv sync --frozen

EXPOSE 8501

CMD ["uv", "run", "streamlit", "run", "app.py", "--server.port=8501", "--server.address=0.0.0.0"]
