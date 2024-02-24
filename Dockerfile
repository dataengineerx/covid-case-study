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
COPY helloworld/ ./helloworld
COPY helloworld/requirements.txt helloworld/requirements.txt

#set PYTHONPATH for python location
RUN export PYTHONPATH=/usr/local/lib/python3.11/

RUN python --version

#mkdir folder                                   
RUN mkdir -p /app/data

#expose port 8000
EXPOSE 8000

#run the application
CMD ["poetry", "run", "uvicorn", "helloworld.main:app", "--host", "0.0.0.0", "--port", "8000"]

