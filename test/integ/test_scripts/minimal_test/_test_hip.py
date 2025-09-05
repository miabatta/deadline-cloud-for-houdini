# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import argparse
import os
import sys

import hou

from deadline_cloud_for_houdini.submitter import _create_job_bundle  # type: ignore
from deadline_cloud_for_houdini._assets import _get_evaluated_asset_references, _parse_files  # type: ignore
from test.integ.helpers import hip_utils


def build_scene(output_dir: str):
    geo_node = hip_utils.create_box_geometry("test_geo")
    cam_node = hip_utils.create_camera("test_cam", translate=(5, 5, 5), lookat_node=geo_node)
    hip_utils.create_light("test_light", translate=(1, 1, 2))
    render_node = hip_utils.create_mantra(
        "mantra1", cam_node=cam_node, output_file=f"{output_dir}/$HIPNAME.$OS.$F4.png"
    )
    submitter_node = hip_utils.create_submitter("submitter_node", input_node=render_node)

    hip_utils.create_keyframes(node=cam_node, parm_name="tx", values=[5, 5.5])

    hou.hipFile.setName("test.hip")

    return submitter_node


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("job_history_dir")
    parser.add_argument("output_dir")
    parser.add_argument("test_type", type=str, choices=["submitter", "adaptor"])
    args = parser.parse_args(args=sys.argv[sys.argv.index("--") :])

    # We want to use the same scene for both submitter and adaptor tests.
    # Depending on which test, we have different uses for the scene file:
    # Either use the submitter node to generate a job bundle,
    # or save the scene for use in an `openjd run` call.
    submitter_node = build_scene(args.output_dir)
    if args.test_type == "submitter":
        _parse_files(submitter_node)
        _create_job_bundle(
            submitter_node, args.job_history_dir, _get_evaluated_asset_references(submitter_node)
        )
    elif args.test_type == "adaptor":
        hou.hipFile.save(os.path.join(args.output_dir, "test.hip"))
