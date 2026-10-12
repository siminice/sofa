FROM mcr.microsoft.com/playwright/python:v1.55.0-noble
RUN pip install playwright==1.55.0
COPY sofa_token.py /sofa_token.py
ENTRYPOINT ["xvfb-run", "-a", "python", "/sofa_token.py"]
