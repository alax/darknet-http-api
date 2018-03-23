FROM nvidia/cuda:8.0-devel

WORKDIR /app

RUN apt-get update && \
    apt-get install -y \
    build-essential libopencv-dev git python python-pip python-dev wget

# Upgrade PIP
RUN pip install --upgrade pip && \
    pip install --upgrade virtualenv

COPY ./blob/coco.data /app/blob/coco.data

# Download the latest version of Darknet
RUN git clone https://github.com/pjreddie/darknet.git
RUN wget https://pjreddie.com/media/files/yolo.weights -O /app/blob/yolo.weights

# Compile Darknet
RUN cd /app/darknet/ && \
    make OPENCV=1 GPU=1

# Add files with corrected paths to Darknet
RUN mv /app/blob/coco.data /app/darknet/cfg/coco.data

COPY ./requirements.txt /app/

# Install python dependencies
RUN pip install -r requirements.txt
RUN mkdir /app/uploads/

COPY ./darknet.py /app/
COPY ./app.py /app/

EXPOSE 5000

CMD [ "gunicorn", "-b 0.0.0.0:5000", "-w 4", "app:APP" ]
