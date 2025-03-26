python phc/run_hydra.py project_name=Robot_IM robot=unitree_g1 \
  env=env_im_g1_phc env.motion_file=sample_data/dance_sample_g1.pkl \
  learning=im_pnn_big exp_name=unitree_g1_pnn sim=robot_sim control=robot_control \
  learning.params.network.space.continuous.sigma_init.val=-1.7
