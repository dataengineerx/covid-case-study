#use python image 
FROM python:3.11.7-slim

RUN apt-get update \
    && apt-get install --no-install-recommends -y \
        # deps for installing poetry
        curl \
        # deps for building python deps
        build-essential

#set working directory
WORKDIR /app

#copy all files from current directory to working directory
COPY src/ ./src
COPY test/ ./test
COPY poetry.lock pyproject.toml ./

#set PYTHONPATH for python location
RUN export PYTHONPATH=/usr/local/lib/python3.11/

RUN python --version

#set poetry path
ENV POETRY_HOME="/opt/poetry" \
    POETRY_VIRTUALENVS_IN_PROJECT=true \
    POETRY_NO_INTERACTION=1 

ENV PATH="$POETRY_HOME/bin:$VENV_PATH/bin:$PATH"

RUN curl -sSL https://install.python-poetry.org | python -

RUN poetry install --no-dev

#mkdir folder                                   
RUN mkdir -p /app/data

#expose port 8000
EXPOSE 8000

#run the application
CMD ["poetry", "run", "uvicorn", "src.main:app", "--host", "0.0.0.0", "--port", "8000"]

