FROM python:3.8-alpine
WORKDIR /app
COPY requirements.txt /app/requirements.txt
RUN apk --no-cache add gcc musl-dev libffi-dev openssl-dev python3-dev build-base
RUN pip install --no-cache-dir -r requirements.txt
COPY . .
CMD uvicorn main:app --host localhost --port 8000 --reload