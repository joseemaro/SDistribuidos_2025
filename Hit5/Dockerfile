FROM python:3.9

WORKDIR /app

COPY program_c.py .

COPY .env.node1 .
COPY .env.node2 .

RUN pip install python-dotenv

ENV PYTHONUNBUFFERED=1

CMD ["python", "program_c.py"]
