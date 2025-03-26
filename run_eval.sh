python phc/run_hydra.py learning=im_mcp_big exp_name=phc_comp_3 env=env_im_getup_mcp \
  robot=smpl_humanoid env.zero_out_far=False robot.real_weight_porpotion_boxes=False \
  env.num_prim=3 env.motion_file=sample_data/amass_isaac_standing_upright_slim.pkl \
  env.models="[output/HumanoidIm/phc_3/Humanoid.pth]" env.num_envs=1 headless=True \
  im_eval=False env.num_envs=1 learning.params.config.minibatch_size=32 \
  learning.params.config.amp_minibatch_size=32 num_threads=1 headless=False test=True \
  epoch=117500
