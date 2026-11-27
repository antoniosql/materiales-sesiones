FROM python:3.12-slim
WORKDIR /app
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt
COPY server.py .
# Los permisos del contexto dependen del sistema que construye: legibles para el usuario 1000
RUN chmod -R a+rX /app
ENV PORT=8000 PYTHONUNBUFFERED=1
EXPOSE 8000
USER 1000
CMD ["python", "server.py"]
