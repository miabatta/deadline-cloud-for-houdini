# Copyright Amazon.com, Inc. or its affiliates. All Rights Reserved.

"""
Wrappers around the Houdini API for node operations common to Houdini integration tests.
Some wrappers have built-in parameter setting based off arguments;
to set any other parameters, use **kwargs or call the Houdini API directly.
"""

import hou

from typing import Optional

DEFAULT_SUBMITTER_SETTINGS = {
    "name": "$HIPNAME",
    "separate_steps": 1,
    "include_adaptor_wheels": 0,
    "auto_unlock_rops": 0,
    "auto_parse_hip": 0,
    "auto_save_hip": 0,
    "trange": 2,
}


def _add_kwargs(node, kwargs) -> None:
    """
    Use **kwargs from a function call to set extra parameters on a node.
    """

    for name, value in kwargs.items():
        try:
            node.parm(name).set(value)
        except Exception as e:
            print(f'Could not set parameter "{name}" :\n{e}')


def create_box_geometry(
    name: str, translate: tuple[float, float, float] = (0, 0, 0), **kwargs
) -> hou.SopNode:
    geo_node = hou.node("/obj").createNode("geo", name)
    geo_node.createNode("box")

    if translate:
        geo_node.setParmTransform(hou.hmath.buildTransform(*translate))

    _add_kwargs(geo_node, kwargs)
    return geo_node


def create_camera(
    name: str,
    translate: tuple[float, float, float] = (0, 0, 0),
    lookat_node: Optional[hou.Node] = None,
    **kwargs,
) -> hou.ObjNode:
    cam_node = hou.node("/obj").createNode("cam", name)

    if len(translate) < 3:
        raise RuntimeError(
            f'Camera node "{name}" must use a 3-tuple for translation.\nGiven: {translate}'
        )

    cam_node.setParmTransform(hou.hmath.buildTranslate(*translate))

    if lookat_node:
        cam_node.setWorldTransform(cam_node.buildLookatRotation(lookat_node))

    _add_kwargs(cam_node, kwargs)
    return cam_node


def create_light(
    name: str,
    translate: tuple[float, float, float] = (0, 0, 0),
    colour: Optional[tuple[float]] = None,
    **kwargs,
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

    _add_kwargs(light_node, kwargs)
    return light_node


def create_mantra(name: str, cam_node: hou.ObjNode, output_file: str, **kwargs) -> hou.RopNode:
    render_node = hou.node("/out").createNode("ifd", name)

    render_node.parm("camera").set(cam_node.path())
    render_node.parm("vm_picture").set(output_file)
    _add_kwargs(render_node, kwargs)
    return render_node


def create_submitter(name: str, input_node: hou.RopNode, **kwargs) -> hou.RopNode:
    submitter_node = hou.node("/out").createNode("deadline_cloud", name)
    submitter_node.setFirstInput(input_node)
    _add_kwargs(submitter_node, kwargs)
    return submitter_node


def create_keyframes(node: hou.Node, parm_name: str, values: list) -> None:
    kf_parm = hou.parm(f"{node.path()}/{parm_name}")
    kf_list = []

    for i in range(len(values)):
        curr_frame = hou.Keyframe(values[i])
        curr_frame.setFrame(i + 1)
        kf_list.append(curr_frame)

    kf_parm.setKeyframes(kf_list)

    hou.playbar.setFrameRange(1, len(values))


def create_toon_shader(
    name: str,
    high_colour: tuple[float, float, float] = (1, 1, 1),
    mid_colour: tuple[float, float, float] = (1, 1, 1),
    low_colour: tuple[float, float, float] = (1, 1, 1),
    **kwargs,
) -> hou.VopNode:
    shader_node = hou.node("/mat").createNode("tooncolorshader", name)

    shader_node.parm("colorhighr").set(high_colour[0])
    shader_node.parm("colorhighg").set(high_colour[1])
    shader_node.parm("colorhighb").set(high_colour[2])

    shader_node.parm("colormidr").set(mid_colour[0])
    shader_node.parm("colormidg").set(mid_colour[1])
    shader_node.parm("colormidb").set(mid_colour[2])

    shader_node.parm("colorlowr").set(low_colour[0])
    shader_node.parm("colorlowg").set(low_colour[1])
    shader_node.parm("colorlowb").set(low_colour[2])

    _add_kwargs(shader_node, kwargs)
    return shader_node


def create_wedge_node(
    name: str, output_driver: hou.RopNode, num_wedgeparams: int, **kwargs
) -> hou.RopNode:
    wedge_node = hou.node("/out").createNode("wedge", name)
    wedge_node.parm("driver").set(output_driver.path())
    wedge_node.parm("wedgeparams").set(num_wedgeparams)

    for i in range(num_wedgeparams):
        wedge_node.parm(f"range{i}x").set(0)
        wedge_node.parm(f"range{i}y").set(1)
        wedge_node.parm(f"steps{i}").set(2)

    _add_kwargs(wedge_node, kwargs)
    return wedge_node
