FROM continuumio/miniconda:latest
MAINTAINER Ricardo R. da Silva <ridasilva@usp.br>

ENV INSTALL_PATH /formatdb_flask
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY environment.yml environment.yml
RUN conda env create -f environment.yml
RUN echo "source activate formatdb" > ~/.bashrc
ENV PATH /opt/conda/envs/formatdb/bin:$PATH

COPY . .
RUN pip install markupsafe==2.0.1
RUN pip install werkzeug==0.16.0 

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "api.upload:app"
#CMD ["gunicorn", "-c", "python:config.gunicorn", "api.upload:app"]

