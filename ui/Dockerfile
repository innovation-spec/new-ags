FROM python:3.12-slim
WORKDIR /ui
COPY ui/pyproject.toml ./pyproject.toml
RUN pip install --no-cache-dir .
COPY ui .
EXPOSE 8501
CMD ["streamlit", "run", "app.py", "--server.address=0.0.0.0", "--server.port=8501"]
