FROM nikolaik/python-nodejs:latest

# Install browsers
RUN apt-get update && apt-get install -y \
    chromium-driver firefox-esr \
    ca-certificates libmagic1 \
    curl jq wget git ffmpeg

# Install the required python packages globally
ENV PATH="$PATH:/root/.local/bin"
ENV PYTHONPATH=/src
ENV PLUGINS_DIR=/plugins

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
RUN mkdir ${PLUGINS_DIR}
RUN mkdir /src
RUN curl -L -o ${PLUGINS_DIR}/Auto-GPT-Plugins.zip https://github.com/Significant-Gravitas/Auto-GPT-Plugins/archive/refs/heads/master.zip
RUN curl -L -o ${PLUGINS_DIR}/AutoGPT_Slack.zip https://github.com/adithya77/Auto-GPT-slack-plugin/archive/refs/heads/main.zip
RUN curl -L -o ${PLUGINS_DIR}/AutoGPT_YouTube.zip https://github.com/Yolley/AutoGPT-YouTube/archive/refs/heads/master.zip

ARG AUTO_GPT_VERSION
ENV AUTO_GPT_VERSION ${AUTO_GPT_VERSION}

RUN curl -L -o auto_gpt.zip https://github.com/Significant-Gravitas/Auto-GPT/archive/refs/tags/v${AUTO_GPT_VERSION}.zip \
    && unzip auto_gpt.zip \
    && cd "Auto-GPT-${AUTO_GPT_VERSION}" \
    && mv autogpt /src/ \
    && pip install -r requirements.txt \
    && python scripts/check_requirements.py requirements.txt \
    && python scripts/install_plugin_deps.py

COPY ./src/ /src/
COPY ./migrations /migrations
COPY ./prisma_partial /prisma_partial
COPY ./schema.prisma /schema.prisma

COPY entrypoint.sh /entrypoint.sh
COPY gunicorn_conf.py /gunicorn_conf.py
COPY backend_pre_start.py /backend_pre_start.py

RUN chmod +x /entrypoint.sh

ENTRYPOINT ["/entrypoint.sh"]
