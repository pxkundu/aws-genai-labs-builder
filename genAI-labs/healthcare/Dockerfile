# Healthcare ChatGPT Clone - OpenWebUI Dockerfile
# This Dockerfile customizes OpenWebUI for healthcare use cases

FROM ghcr.io/open-webui/open-webui:main

# Set working directory
WORKDIR /app

# Install additional Python packages for healthcare functionality
RUN pip install --no-cache-dir \
    boto3==1.34.0 \
    psycopg2-binary==2.9.9 \
    sqlalchemy==2.0.23 \
    fastapi==0.104.1 \
    pydantic==2.5.0 \
    python-dotenv==1.0.0

# Copy custom healthcare configurations
COPY frontend/custom/ /app/frontend/custom/
COPY data/knowledge_base/ /app/data/knowledge_base/

# Copy custom healthcare themes
COPY frontend/custom/themes/ /app/frontend/custom/themes/

# Copy custom healthcare components
COPY frontend/custom/components/ /app/frontend/custom/components/

# Set environment variables for healthcare customization
ENV HEALTHCARE_MODE=true
ENV CUSTOM_THEME=healthcare
ENV ENABLE_HEALTHCARE_FEATURES=true

# Expose port
EXPOSE 8080

# Health check
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl -f http://localhost:8080/health || exit 1

# Start OpenWebUI with healthcare customizations
CMD ["python", "-m", "uvicorn", "open_webui.main:app", "--host", "0.0.0.0", "--port", "8080"]
