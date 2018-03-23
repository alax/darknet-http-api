# darknet-http-api
*Easy-to-use, language agnostic image object detection.*

### Motivation
This project aims to make it easy for anyone to use Darknet and YOLOv2 via a simple HTTP API. Setting up and configuring YOLOv2 isn’t too difficult on it’s own, but once you add OpenCL and CUDA support, things become more tricky. In addition, by exposing an HTTP interface, developers using any language can easily add object detection to their applications. While this image needs to be deployed on a CUDA-enabled host, your application code can run anywhere, potentially simplifying development and deployment.

### Requirements
At this time, you’ll need a CUDA-enabled host to run the Docker image. The non-CUDA version of YOLOv2 is simply too slow (10s per detection on average, depending on hardware). With CUDA, detection is about 60ms on average (using a Titan X). Much quicker!

If you don’t have nVidia hardware, no problem! [Paperspace](https://www.paperspace.com) makes it easy to deploy GPU-enabled machines, and will perform quite well with this application. I have tested with the P4000 instance, and detection is about 100ms on average, so still very fast. AWS also has GPU machines, but they’re quite a bit more spendy.

I do plan to add support for tiny-yolo, which should massively speed up detection on hosts without CUDA.

### Installation
Unfortunately, due to the CUDA requirement, using this image isn’t as easy as most docker images. If you run the image without installing the nVidia runtime on the host:

```bash
docker run --rm -p 5000:5000 --tmpfs /app/uploads -d alaxander/darknet-http-api
```

You’ll get an error about a missing CUDA driver. CUDA can sometimes be a nightmare to install correctly, so let’s just take the easy route. Using a fresh install of Ubuntu 16.04 LTS, first install some things you’ll need:

```bash
apt-get install wget gnupg-curl
```

Download and install the CUDA repository package:

```bash
wget https://developer.download.nvidia.com/compute/cuda/repos/ubuntu1604/x86_64/cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
dpkg -i cuda-repo-ubuntu1604_8.0.61-1_amd64.deb
```

Install CUDA:
```bash
apt-get update
apt-get install cuda
```

Once that completes, you’ll need to install Docker if you don’t already have it. See that guide:
[Get Docker CE for Ubuntu | Docker Documentation](https://docs.docker.com/install/linux/docker-ce/ubuntu/)

Finally, you’ll just need to install the nVidia runtime for Docker to get CUDA working inside this container. Thankfully, this is also pretty easy using their guide:
https://github.com/NVIDIA/nvidia-docker

See, not that hard at all. If you’ve done all that, you should now be able to run the following command:
```bash
docker run --runtime=nvidia --rm -p 5000:5000 --tmpfs /app/uploads --name darknet-http-api alaxander/darknet-http-api
```
(notice the `—runtime=nvidia` flag)

And the image should start right up! You should be ready to detect objects via the HTTP API now.

### Usage
Once you’ve got the image running, usage is very easy. Simply send a POST to `http://your_docker_host:5000/detect` in `multipart/form-data` format, with your image set as the “file” field. With any luck, you’ll get a quick response back with the data about the objects detected, the confidence in the detection, and the bounding boxes. Here’s example output: (using dog.jpg from the Darknet repository)

```javascript
{
  "status": "ok",
  "matches": [
    {
      "confidence": 0.852813184261322,
      "bounds": {
        "h": 323.8177185058594,
        "w": 493.2893371582031
      },
      "name": "bicycle",
      "center": {
        "y": 286.02069091796875,
        "x": 341.571044921875
      }
    },
    {
      "confidence": 0.8236840963363647,
      "bounds": {
        "h": 289.33984375,
        "w": 189.18247985839844
      },
      "name": "dog",
      "center": {
        "y": 376.65716552734375,
        "x": 226.77752685546875
      }
    },
    {
      "confidence": 0.6522704362869263,
      "bounds": {
        "h": 84.02362060546875,
        "w": 212.5281982421875
      },
      "name": "truck",
      "center": {
        "y": 126.1904067993164,
        "x": 573.9798583984375
      }
    }
  ],
  "perf": 71
}
```
