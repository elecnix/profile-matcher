FROM python:3.12-slim
WORKDIR /app
COPY pyproject.toml ./
RUN pip install uv && uv sync
WORKDIR /app/services/campaigns
COPY services/campaigns .
ENV PYTHONPATH=/app
CMD ["uv", "run", "uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
