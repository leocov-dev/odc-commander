from typing import Annotated, Literal

from pydantic import BaseModel, Field

from odc_commander.commands.basic_params import FloatParam


class RuntimeComponentData(BaseModel):
    """"""

    component_type: Literal["runtime"]
    params: list[FloatParam]


class InputCalibrationComponentData(BaseModel):
    """"""

    component_type: Literal["calibration_input"]


class OutputCalibrationComponentData(BaseModel):
    """"""

    component_type: Literal["calibration_output"]


ProjectComponentData = Annotated[
    RuntimeComponentData | InputCalibrationComponentData | OutputCalibrationComponentData,
    Field(discriminator="component_type"),
]
