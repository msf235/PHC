# FROM nvcr.io/nvidia/pytorch:21.09-py3
# use 23.02 version which has cuda 12.0.1 with pytorch 1.14 in ubunut 20.4
# see https://docs.nvidia.com/deeplearning/frameworks/pytorch-release-notes
FROM nvcr.io/nvidia/pytorch:23.02-py3

ENV DEBIAN_FRONTEND=noninteractive 

ENV NVM_DIR=/usr/local/nvm
RUN mkdir -p $NVM_DIR
RUN curl -o- https://raw.githubusercontent.com/creationix/nvm/v0.33.1/install.sh | bash
ENV NODE_VERSION=v18.20.4
RUN /bin/bash -c "source $NVM_DIR/nvm.sh && nvm install $NODE_VERSION && nvm use --delete-prefix $NODE_VERSION"

ENV NODE_PATH=$NVM_DIR/versions/node/$NODE_VERSION/lib/node_modules
ENV PATH=$NVM_DIR/versions/node/$NODE_VERSION/bin:$PATH

#RUN rm -rf /usr/local/nvm/*
##ENV NVM_DIR="$HOME/.nvm"

#RUN curl -o- https://raw.githubusercontent.com/nvm-sh/nvm/v0.40.1/install.sh | bash

##RUN export NVM_DIR="$HOME/.nvm"
#RUN [ -s "$NVM_DIR/nvm.sh" ] && \. "$NVM_DIR/nvm.sh"  # This loads nvm
#RUN [ -s "$NVM_DIR/bash_completion" ] && \. "$NVM_DIR/bash_completion"  # This loads nvm bash_completion

# dependencies for gym
#
RUN apt-get update \
 && apt-get install -y --no-install-recommends \
 libxcursor-dev \
 libxrandr-dev \
 libxinerama-dev \
 libxi-dev \
 mesa-common-dev \
 zip \
 unzip \
 make \
 gcc-9 \
 g++-8 \
 vulkan-utils \
 mesa-vulkan-drivers \
 pigz \
 git \
 libegl1 \
 git-lfs \
 sudo \
 libosmesa6-dev \
 xserver-xephyr \
 x11-apps \
 tmux \
 zsh \
 fzf \
 software-properties-common \
 python3-venv \
 openssh-client \
 && apt-get clean

# Force gcc 8 to avoid CUDA 10 build issues on newer base OS
#RUN update-alternatives --install /usr/bin/gcc gcc /usr/bin/gcc-8 8
#RUN update-alternatives --install /usr/bin/g++ g++ /usr/bin/g++-8 8

# WAR for eglReleaseThread shutdown crash in libEGL_mesa.so.0 (ensure it's never detected/loaded)
# Can't remove package libegl-mesa0 directly (because of libegl1 which we need)
RUN rm /usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0 /usr/lib/x86_64-linux-gnu/libEGL_mesa.so.0.0.0 /usr/share/glvnd/egl_vendor.d/50_mesa.json

COPY docker/nvidia_icd.json /usr/share/vulkan/icd.d/nvidia_icd.json
COPY docker/10_nvidia.json /usr/share/glvnd/egl_vendor.d/10_nvidia.json

RUN add-apt-repository ppa:neovim-ppa/unstable
RUN apt-get update
RUN apt-get install -y --no-install-recommends neovim

WORKDIR /opt/isaacgym

# Add non-root user and add it to non-password sudoers
RUN useradd --create-home gymuser
RUN adduser gymuser sudo
RUN echo '%sudo ALL=(ALL) NOPASSWD:ALL' >> /etc/sudoers

USER gymuser

# dependency do not conflict pytorch
RUN pip install --upgrade pip &&  pip install --no-cache-dir gdown mujoco numpy-stl vtk patchelf termcolor scikit-image numpy  scipy ipdb 'joblib>=1.2.0' \
 'lsprotocol==2023.0.1' \
 opencv-python==4.6.0.66 \
 tqdm \
 pyyaml \
 wandb \
 scikit-image \
 gym \
 git+https://github.com/ZhengyiLuo/smplx.git@master \
 lxml \
 human_body_prior \
 autograd \
 scikit-learn \
 chumpy \
 wandb \
 pyvirtualdisplay \
 chardet \
 cchardet \
 geoopt \ 
 imageio-ffmpeg \
 easydict \
 open3d \
 torchgeometry \
 pytorch_lightning \
 pynvim \
 neovim \
 ipdb \
 pdbpp \
 rl-games==1.1.4 

RUN npm install -g neovim
    
ENV NVIDIA_VISIBLE_DEVICES=all NVIDIA_DRIVER_CAPABILITIES=all
ENV PATH "$PATH:/home/gymuser/.local/bin"

WORKDIR /home/gymuser
RUN cd

RUN mv .bashrc .bashrc_bk

# copy gym repo to docker
#COPY --chown=gymuser . .
COPY --chown=gymuser SMPLSim SMPLSim
RUN cd SMPLSim/ && pip install -e .
RUN cd
COPY --chown=gymuser python python
# install gym modules
ENV PATH="/home/gymuser/.local/bin:$PATH"
RUN cd python && pip install -q -e .
RUN cd
RUN sh -c "$(curl -fsSL https://raw.githubusercontent.com/ohmyzsh/ohmyzsh/master/tools/install.sh)"
RUN sh -c 'curl -fLo "${XDG_DATA_HOME:-$HOME/.local/share}"/nvim/site/autoload/plug.vim --create-dirs \
       https://raw.githubusercontent.com/junegunn/vim-plug/master/plug.vim'
COPY --chown=gymuser config_files ./
RUN git clone https://github.com/zsh-users/zsh-autosuggestions ${ZSH_CUSTOM:-~/.oh-my-zsh/custom}/plugins/zsh-autosuggestions
# RUN nvim -u /home/gymuser/.config/nvim/pluginstall_init.vim --headless +PlugInstall +qall
# RUN nvim --headless +'CocInstall -sync coc-snippets|qa'
COPY --chown=gymuser PerpetualHumanoidControl PerpetualHumanoidControl
COPY --chown=gymuser assets assets
COPY --chown=gymuser docs docs
COPY --chown=gymuser licenses licenses
COPY --chown=gymuser README.txt README.txt
COPY --chown=gymuser create_conda_env_rlgpu.sh create_conda_env_rlgpu.sh
COPY amass amass
# COPY --chown=gymuser AMASS AMASS

