python phc/run_hydra.py learning=im_big exp_name=amass_single_example env=env_im robot=smpl_humanoid \
  env.motion_file=sample_data/amass_single_example_upright.pkl \
  num_threads=1 headless=False test=True epoch=-1 env.num_envs=1
