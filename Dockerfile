FROM python:3.10
WORKDIR /app
COPY . .
RUN python -m pip install -r requirements.txt && python -m pip install -r ldv_watcher/requirements.txt
ENTRYPOINT ["python"]
CMD ["watch.py"]
