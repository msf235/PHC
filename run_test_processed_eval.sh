python phc/run_hydra.py learning=im_mcp_big exp_name=test_mujoco env=env_im_getup_mcp \
  robot=smpl_humanoid env.zero_out_far=False robot.real_weight_porpotion_boxes=False \
  env.motion_file=./sample_data/test_processed_smpl_data.pkl \
  num_threads=1 headless=False test=True env.num_envs=1 epoch=-1
