FROM python:3.13-slim

ENV DASH_DEBUG_MODE False
ENV PYTHONUNBUFFERED=1

WORKDIR /app

COPY src/requirements.txt requirements.txt
RUN pip install -r requirements.txt

COPY src/ .

EXPOSE 8050

CMD ["gunicorn", "-b", "0.0.0.0:8050", "--reload", "app:server"]
