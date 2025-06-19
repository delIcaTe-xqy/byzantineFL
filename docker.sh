nvidia-docker run -d -it --restart always --name experiment --shm-size 256G -p 10001:10001 --ip=0.0.0.0 -v type=bind,source=$(pwd)/tmi,target=/root/tmi pytorch/pytorch:1.12.0-cuda11.3-cudnn8-devel
