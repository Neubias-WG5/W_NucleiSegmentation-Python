FROM neubiaswg5/neubias-base

ADD wrapper.py /app/wrapper.py
ADD script.py /app/script.py

# for running the wrapper locally
ADD descriptor.json /app/descriptor.json

ENTRYPOINT ["python", "/app/wrapper.py"]