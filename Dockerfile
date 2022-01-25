FROM python:3
WORKDIR /usr/src/app
COPY . .
ENV TOKEN=
ENV MESSAGE_ID=
ENV RESUME_CHANNEL=
ENV SUBMISSION_CHANNEL=
RUN pip install -r requirements.txt
CMD ["main.py"]
ENTRYPOINT ["python3"]