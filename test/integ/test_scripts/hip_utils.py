# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

import hou

from typing import Any, Optional

DEFAULT_SUBMITTER_SETTINGS = {
    "name": "$HIPNAME",
    "separate_steps": 1,
    "include_adaptor_wheels": 0,
    "auto_unlock_rops": 0,
    "auto_parse_hip": 0,
    "auto_save_hip": 0,
    "trange": 2,
}


def create_box_geometry(
    name: str, translate: tuple[float, float, float] = (0, 0, 0)
) -> hou.SopNode:
    geo_node = hou.node("/obj").createNode("geo", name)
    geo_node.createNode("box")

    return geo_node


def create_camera(
    name: str,
    translate: tuple[float, float, float] = (0, 0, 0),
    lookat_node: Optional[hou.Node] = None,
) -> hou.ObjNode:
    cam_node = hou.node("/obj").createNode("cam", name)

    if len(translate) < 3:
        raise RuntimeError(
            f'Camera node "{name}" must use a 3-tuple for translation.\nGiven: {translate}'
        )

    cam_node.setParmTransform(hou.hmath.buildTranslate(*translate))

    if lookat_node:
        cam_node.setWorldTransform(cam_node.buildLookatRotation(lookat_node))

    return cam_node


def create_light(
    name: str,
    translate: tuple[float, float, float] = (0, 0, 0),
    colour: Optional[tuple[float]] = None,
) -> hou.ObjNode:
    light_node = hou.node("/obj").createNode("hlight", name)

    if len(translate) < 3:
        raise RuntimeError(
            f'Light node "{name}" must use a 3-tuple for translation.\nGiven: {translate}'
        )

    light_node.setParmTransform(hou.hmath.buildTranslate(*translate))

    if colour and len(colour) == 3:
        light_node.parm("light_colorr").set(colour[0])
        light_node.parm("light_colorg").set(colour[1])
        light_node.parm("light_colorb").set(colour[2])

    return light_node


def create_mantra(name: str, cam_node: hou.ObjNode, output_dir: str) -> hou.RopNode:
    render_node = hou.node("/out").createNode("ifd", name)

    render_node.parm("camera").set(cam_node.path())
    render_node.parm("vm_picture").set(output_dir)

    return render_node


def create_submitter(
    name: str, input_node: hou.RopNode, params: dict[str, Any] = DEFAULT_SUBMITTER_SETTINGS
) -> hou.RopNode:
    submitter_node = hou.node("/out").createNode("deadline_cloud", name)

    submitter_node.setFirstInput(input_node)
    for param, val in params.items():
        try:
            submitter_node.parm(param).set(val)
        except AttributeError as ae:  # i.e., parm with this name does not exist
            raise RuntimeError(f'Submitter node has no parameter "{param}."\nError message: {ae}')

    return submitter_node


def create_keyframes(node: hou.Node, parm_name: str, values: list) -> None:
    kf_parm = hou.parm(f"{node.path()}/{parm_name}")
    kf_list = []

    for i in range(len(values)):
        kf_list.append(hou.Keyframe().setFrame(i).setValue(values[i]))

    kf_parm.setKeyframes(kf_list)

    hou.playbar.setRange(len(values))
