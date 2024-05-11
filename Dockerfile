FROM umihico/aws-lambda-selenium-python:latest

COPY requirements.txt ${LAMBDA_TASK_ROOT}
RUN pip install -r requirements.txt

COPY config.ini ${LAMBDA_TASK_ROOT}
COPY keyfile.json* ${LAMBDA_TASK_ROOT}
COPY handler.py ${LAMBDA_TASK_ROOT}
COPY utils.py ${LAMBDA_TASK_ROOT}
COPY visa.py ${LAMBDA_TASK_ROOT}

CMD [ "handler.lambda_handler" ]