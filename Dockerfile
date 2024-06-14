FROM python:3.10.11

EXPOSE 5000

WORKDIR /app

COPY ./requirements.txt /app/requirements.txt

RUN pip install --no-cache-dir --upgrade -r /app/requirements.txt

COPY ./app /app/app

HEALTHCHECK --interval=5s --timeout=5s --retries=3 \
    CMD wget -nv -t1 --spider 'http://localhost:5000/' || exit 1

CMD ["uvicorn", "app.main:app", "--host", "0.0.0.0", "--port", "5000"]