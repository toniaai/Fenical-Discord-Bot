FROM python:latest
ADD . /Fenical-Discord-Bot

RUN cd Fenical-Discord-Bot && \
    pip install -r requirements.txt

CMD ["/Fenical-Discord-Bot/run_linuxmac.sh"]
