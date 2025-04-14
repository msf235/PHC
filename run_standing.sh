python phc/run_hydra.py learning=im_mcp_big exp_name=standing env=env_im_getup_mcp \\
robot=smpl_humanoid env.zero_out_far=False robot.real_weight_porpotion_boxes=False \\
env.motion_file=sample_data/amass_isaac_standing_upright_slim.pkl \\
env.models=[output/HumanoidIm/phc_3/Humanoid.pth] headless=True \\
