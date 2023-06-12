FROM nikolaik/python-nodejs:latest

# Install browsers
RUN apt-get update && apt-get install -y \
    chromium-driver firefox-esr \
    ca-certificates libmagic1 \
    curl jq wget git

# Install the required python packages globally
ENV PATH="$PATH:/root/.local/bin"

# Configure Poetry
RUN poetry config virtualenvs.create false

# Install Prisma CLI
RUN npm install -g prisma@4.11.0
ENV PRISMA_BINARY_CACHE_DIR=/usr/lib/

# Copy using poetry.lock* in case it doesn't exist yet
COPY ./pyproject.toml ./poetry.lock* /
WORKDIR /

RUN poetry run pip install --upgrade pip
RUN poetry install --no-root --only main
RUN git clone -b stable https://github.com/Significant-Gravitas/Auto-GPT.git \
    && cd Auto-GPT \
    && pip install -r requirements.txt

COPY ./src /src
COPY ./migrations /migrations
COPY ./prisma_partial /prisma_partial
COPY ./schema.prisma /schema.prisma

RUN mv /Auto-GPT/autogpt /src/
ENV PYTHONPATH /src

COPY entrypoint.sh /entrypoint.sh
COPY gunicorn_conf.py /gunicorn_conf.py
COPY backend_pre_start.py /backend_pre_start.py

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
