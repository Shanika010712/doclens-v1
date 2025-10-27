FROM public.ecr.aws/lambda/python:3.11


RUN yum update -y && yum install -y \
    epel-release \
    poppler-utils \
    tesseract \
    && yum clean all


# Ensure Tesseract is in the PATH
ENV PATH="/usr/bin:${PATH}"

# Set working directory
WORKDIR ${LAMBDA_TASK_ROOT}

# Copy requirements.txt and install dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy function code
COPY . .

# Set CMD to your Lambda function handler
CMD ["lambda_function.lambda_handler"]