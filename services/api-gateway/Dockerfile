# Forge API gateway image (FR-P5: signed images, SBOM published at release time).
FROM python:3.11-slim

WORKDIR /app

# Install the shared lib then the service (editable path source resolved at build).
COPY libs/forge-common /libs/forge-common
COPY services/api-gateway /app

RUN pip install --no-cache-dir /libs/forge-common && \
    pip install --no-cache-dir .

EXPOSE 8000
CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "8000"]
