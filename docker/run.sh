#!/bin/bash
set -e
set -u

CONTAINER_NAME=isaacgym_container

if docker container ls -a | grep -q $CONTAINER_NAME; then
  docker start $CONTAINER_NAME
  echo "Container $CONTAINER_NAME is running. Attaching."
  docker exec -it $CONTAINER_NAME /bin/bash
  exit 0
fi

if [ $# -eq 0 ]; then
  echo "running docker without display"
  docker run -it --network=host --gpus=all --ipc=host --ulimit memlock=-1 --ulimit stack=67108864 --name=$CONTAINER_NAME \
    -v $HOME/projects/isaacgym_phc/PerpetualHumanoidControl:/home/gymuser/PerpetualHumanoidControl \
    isaacgym /bin/bash
else
  export DISPLAY=$DISPLAY
  echo "setting display to $DISPLAY"
  xhost +
  docker run -it -v /tmp/.X11-unix:/tmp/.X11-unix \
    -v $HOME/projects/isaacgym_phc/PerpetualHumanoidControl:/home/gymuser/PerpetualHumanoidControl \
    -v /storage/amass:/home/gymuser/amass \
    -e DISPLAY=$DISPLAY -w /home/gymuser/PerpetualHumanoidControl \
    --network=host --gpus=all --name=$CONTAINER_NAME isaacgym /bin/bash
  --ipc=host --ulimit memlock=-1 --ulimit stack=67108864
  xhost -
fi
