FROM python:3.10-slim

WORKDIR /opt
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1 \
    PIP_NO_CACHE_DIR=1 \
    PYTHONPATH=/opt \
    LANG=C.UTF-8

RUN apt-get update && apt-get install -y --no-install-recommends \
    curl &&  \
    apt-get clean && \
    apt-get autoremove -y && \
    rm -rf /root/.cache &&  \
    rm -rf /var/lib/apt/lists/* && \
    rm -rf /etc/apt/sources.list.d/*

COPY requirements/prod.requirements.txt requirements.txt
RUN python -m pip install --upgrade pip && \
    python -m pip install -r requirements.txt

COPY config config/
COPY xrpl_app xrpl_app/
COPY manage.py .
COPY tests tests/
COPY pytest.ini .
