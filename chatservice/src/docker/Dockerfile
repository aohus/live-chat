FROM aohus/chatservice-base as development

ENV VIRTUMALL_ENV=development
WORKDIR $PYSETUP_PATH

# copy in our built poetry + venv
COPY --from=aohus/chatservice-base $POETRY_HOME $POETRY_HOME
COPY --from=aohus/chatservice-base $PYSETUP_PATH $PYSETUP_PATH

# quicker install as runtime deps are already installed
RUN apt-get update -y && apt-get install iputils-ping -y
COPY src/poetry.lock src/pyproject.toml ./
RUN poetry install

# will become mountpoint of our code
# COPY docker/run_server.sh /opt/pysetup/run_server.sh
# COPY configs/gunicorn.conf.py /opt/pysetup/gunicorn.conf.py
COPY src/ ./
EXPOSE 8000
