FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY src/ .
# Los permisos del contexto dependen del sistema que construye: legibles para el usuario 1000
RUN chmod -R a+rX /app
ENV PYTHONUNBUFFERED=1
USER 1000
CMD ["python", "main.py"]
