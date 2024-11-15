FROM python:3.12-slim
WORKDIR /ui
COPY ui/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir .
COPY ui .
EXPOSE 8501
