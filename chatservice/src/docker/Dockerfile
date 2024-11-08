FROM aohus/chatservice-base as development

WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=aohus/chatservice-base $POETRY_HOME $POETRY_HOME
COPY --from=aohus/chatservice-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN apt-get update -y && apt-get install iputils-ping -y
COPY src/poetry.lock src/pyproject.toml ./
RUN poetry install

# ci pipeline에서 .env file 생성
COPY .env /opt/pysetup/.env
# will become mountpoint of our code
COPY src/ ./
EXPOSE 8000
