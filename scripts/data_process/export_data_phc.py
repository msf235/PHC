import pickle as pkl
import joblib
import numpy as np
from pathlib import Path
from scipy.spatial.transform import Rotation as sRot
import torch
from poselib.poselib.skeleton.skeleton3d import (
    SkeletonTree,
    SkeletonMotion,
    SkeletonState,
)
import argparse
from smpl_sim.smpllib.smpl_joint_names import SMPL_MUJOCO_NAMES, SMPL_BONE_ORDER_NAMES
from smpl_sim.smpllib.smpl_local_robot import SMPL_Robot as LocalRobot

parser = argparse.ArgumentParser()
parser.add_argument("--debug", action="store_true", default=False)
parser.add_argument("--path", type=str, default="")
args = parser.parse_args()


# xquat_mujoco: shape [N, 4] or [N, 24, 4] in MuJoCo format [w, x, y, z]
# Convert to SciPy format [x, y, z, w]
def convert_mujoco_quat_to_scipy(xquat_mujoco):
    return np.concatenate([xquat_mujoco[..., 1:], xquat_mujoco[..., :1]], axis=-1)


# SMPL_BONE_ORDER_NAMES = [
#     "Pelvis",
#     "L_Hip",
#     "R_Hip",
#     "Torso",
#     "L_Knee",
#     "R_Knee",
#     "Spine",
#     "L_Ankle",
#     "R_Ankle",
#     "Chest",
#     "L_Toe",
#     "R_Toe",
#     "Neck",
#     "L_Thorax",
#     "R_Thorax",
#     "Head",
#     "L_Shoulder",
#     "R_Shoulder",
#     "L_Elbow",
#     "R_Elbow",
#     "L_Wrist",
#     "R_Wrist",
#     "L_Hand",
#     "R_Hand",
# ]
#
# SMPL_MUJOCO_NAMES = [
#     "Pelvis",
#     "L_Hip",
#     "L_Knee",
#     "L_Ankle",
#     "L_Toe",
#     "R_Hip",
#     "R_Knee",
#     "R_Ankle",
#     "R_Toe",
#     "Torso",
#     "Spine",
#     "Chest",
#     "Neck",
#     "Head",
#     "L_Thorax",
#     "L_Shoulder",
#     "L_Elbow",
#     "L_Wrist",
#     "L_Hand",
#     "R_Thorax",
#     "R_Shoulder",
#     "R_Elbow",
#     "R_Wrist",
#     "R_Hand",
# ]

# Load configuration and set parameters


upright_start = True

robot_cfg = {
    "mesh": False,
    "rel_joint_lm": True,
    "upright_start": upright_start,
    "remove_toe": False,
    "real_weight": True,
    "real_weight_porpotion_capsules": True,
    "real_weight_porpotion_boxes": True,
    "replace_feet": True,
    "masterfoot": False,
    "big_ankle": True,
    "freeze_hand": False,
    "box_body": False,
    "master_range": 50,
    "body_params": {},
    "joint_params": {},
    "geom_params": {},
    "actuator_params": {},
    "model": "smpl",
}

smpl_local_robot = LocalRobot(
    robot_cfg,
)


def convert_mujoco_to_smpl(qpos):
    # qpos: [N, 76] = 3 (root trans) + 4 (root quat) + 23×3 axis-angle
    N = qpos.shape[0]

    smpl_2_mujoco = [
        SMPL_BONE_ORDER_NAMES.index(q)
        for q in SMPL_MUJOCO_NAMES
        if q in SMPL_BONE_ORDER_NAMES
    ]
    mujoco_2_smpl = [
        SMPL_MUJOCO_NAMES.index(q)
        for q in SMPL_BONE_ORDER_NAMES
        if q in SMPL_MUJOCO_NAMES
    ]

    # Leave off the global translation
    root_trans = qpos[:, :3]  # [N, 3]
    root_orient = sRot.from_quat(qpos[:, 3:7]).as_rotvec()  # [N, 3] <- [N,4]
    pose_aa_mj_flat = np.concatenate((root_orient, qpos[:, 7:]), axis=1)

    pose_aa_mj = pose_aa_mj_flat.reshape(-1, 24, 3)
    # pose_aa_smpl = pose_aa_mj[:, mujoco_2_smpl]
    pose_aa_smpl = pose_aa_mj[:, mujoco_2_smpl]
    pose_aa_smpl_flat = pose_aa_smpl.reshape(N, 72)

    pose_quat = (
        sRot.from_rotvec(pose_aa_smpl.reshape(-1, 3)).as_quat().reshape(N, 24, 4)
    )

    beta = np.zeros((16))
    gender_number, beta[:], gender = [0], 0, "neutral"
    # print("using neutral model")
    #
    smpl_local_robot.load_from_skeleton(
        betas=torch.from_numpy(beta[None,]), gender=gender_number, objs_info=None
    )
    smpl_local_robot.write_xml(f"tmp/tmp_humanoid.xml")
    skeleton_tree = SkeletonTree.from_mjcf(f"tmp/tmp_humanoid.xml")
    root_trans_offset = (
        torch.from_numpy(root_trans) + skeleton_tree.local_translation[0]
    )

    new_sk_state = SkeletonState.from_rotation_and_root_translation(
        skeleton_tree,  # This is the wrong skeleton tree (location wise) here, but it's fine since we only use the parent relationship here.
        torch.from_numpy(pose_quat),
        root_trans_offset,
        is_local=True,
    )

    if robot_cfg["upright_start"]:
        pose_quat_global = (
            (
                sRot.from_quat(new_sk_state.global_rotation.reshape(-1, 4).numpy())
                * sRot.from_quat([0.5, 0.5, 0.5, 0.5]).inv()
            )
            .as_quat()
            .reshape(N, -1, 4)
        )  # should fix pose_quat as well here...

        new_sk_state = SkeletonState.from_rotation_and_root_translation(
            skeleton_tree,
            torch.from_numpy(pose_quat_global),
            root_trans_offset,
            is_local=False,
        )
        pose_quat = new_sk_state.local_rotation.numpy()

        pose_quat_global = new_sk_state.global_rotation.numpy()
        pose_quat = new_sk_state.local_rotation.numpy()

    joint_body_ids = [model.body(name).id for name in SMPL_BONE_ORDER_NAMES]
    pose_quat_global_wxyz = data["xquats"][::skip, joint_body_ids]  # shape: [24, 4]
    pose_quat_global_smpl = convert_mujoco_quat_to_scipy(pose_quat_global_wxyz)

    new_motion_out = {}
    new_motion_out["pose_quat_global"] = pose_quat_global_smpl
    new_motion_out["pose_aa"] = pose_aa_smpl_flat
    new_motion_out["fps"] = 30
    new_motion_out["pose_quat"] = pose_quat
    new_motion_out["trans_orig"] = root_trans
    new_motion_out["root_trans_offset"] = torch.from_numpy(0 * root_trans)
    new_motion_out["beta"] = beta
    new_motion_out["gender"] = "neutral"

    breakpoint()

    return new_motion_out


if __name__ == "__main__":
    # Example usage of the refactored functions
    # ctrls, ctrls_burn_in, env, model, data = run_experiment()
    with open(args.path, "rb") as f:
        data_load = np.load(f)
        # data_load = joblib.load(f)
    # framerate = int(round(1 / model.opt.timestep))
    framerate = int(round(1 / 0.0005))
    skip = int(framerate / 30)
    qpos = data_load[::skip]

    # Initialize environment

    out = convert_mujoco_to_smpl(qpos)
    joblib.dump({"0": out}, "test_processed_smpl_data.pkl")
