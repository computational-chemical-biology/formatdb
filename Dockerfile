FROM continuumio/miniconda:latest
MAINTAINER Ricardo R. da Silva <ridasilva@usp.br>

ENV INSTALL_PATH /formatdb_flask
RUN mkdir -p $INSTALL_PATH
WORKDIR $INSTALL_PATH

COPY environment.yml environment.yml
RUN conda env create -f environment.yml
RUN echo "source activate formatdb" > ~/.bashrc
ENV PATH /opt/conda/envs/formatdb/bin:$PATH

RUN pip install --upgrade pip setuptools
RUN pip install tensorflow
RUN pip install markupsafe==1.1.1
RUN pip install werkzeug==0.15.5
RUN pip install tqdm
RUN pip install joblib 
RUN pip install gevent 
#RUN pip install celery --upgrade
COPY . .
RUN pip install tqdm
RUN conda install conda-forge::tensorflow

CMD gunicorn -b 0.0.0.0:8000 --access-logfile - "api.upload:app"
#CMD ["gunicorn", "-c", "python:config.gunicorn", "api.upload:app"]

