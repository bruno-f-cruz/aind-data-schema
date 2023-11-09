""" Schemas for Neurophysiology and Behavior Rigs"""

from __future__ import annotations

from datetime import date
from typing import List, Optional, Union

from pydantic import Field, root_validator
from pydantic.typing import Annotated

from aind_data_schema.base import AindCoreModel
from aind_data_schema.data_description import Modality
from aind_data_schema.device import (
    Calibration,
    CameraAssembly,
    DAQDevice,
    Detector,
    Device,
    DigitalMicromirrorDevice,
    Disc,
    EphysAssembly,
    Filter,
    HarpDevice,
    Laser,
    LaserAssembly,
    Lens,
    LightEmittingDiode,
    Monitor,
    NeuropixelsBasestation,
    Objective,
    Olfactometer,
    OpenEphysAcquisitionBoard,
    Patch,
    PockelsCell,
    PolygonalScanner,
    RewardDelivery,
    Speaker,
    StickMicroscopeAssembly,
    Treadmill,
    Tube,
    Wheel,
)

devices = [Calibration,
    CameraAssembly,
    DAQDevice,
    Detector,
    Device,
    DigitalMicromirrorDevice,
    Disc,
    EphysAssembly,
    Filter,
    HarpDevice,
    Laser,
    LaserAssembly,
    Lens,
    LightEmittingDiode,
    Monitor,
    NeuropixelsBasestation,
    Objective,
    Olfactometer,
    OpenEphysAcquisitionBoard,
    Patch,
    PockelsCell,
    PolygonalScanner,
    RewardDelivery,
    Speaker,
    StickMicroscopeAssembly,
    Treadmill,
    Tube,
    Wheel,
]

class Rig(AindCoreModel):
    """Description of a rig"""

    schema_version: str = Field("0.1.4", description="schema version", title="Version", const=True)
    rig_id: str = Field(..., description="room_stim apparatus_version", title="Rig ID")
    modification_date: date = Field(..., title="Date of modification")
    modalities: List[Modality] = Field(..., title="Modalities", unique_items=True)
    mouse_platform: Annotated[
        Union[Disc, Treadmill, Tube, Wheel], Field(..., title="Mouse platform", discriminator="device_type")
    ]
    stimulus_devices: Optional[
        Annotated[
            List[Union[Monitor, Olfactometer, RewardDelivery, Speaker]],
            Field(None, title="Stimulus devices", unique_items=True, discriminator="device_type"),
        ]
    ]
    cameras: Optional[List[CameraAssembly]] = Field(None, title="Camera assemblies", unique_items=True)
    daqs: Optional[
        Annotated[
            List[Union[HarpDevice, NeuropixelsBasestation, OpenEphysAcquisitionBoard, DAQDevice]],
            Field(None, title="Data acquisition devices", discriminator="device_type"),
        ]
    ]
    ephys_assemblies: Optional[List[EphysAssembly]] = Field(None, title="Ephys probes", unique_items=True)
    stick_microscopes: Optional[List[StickMicroscopeAssembly]] = Field(None, title="Stick microscopes")
    laser_assemblies: Optional[List[LaserAssembly]] = Field(None, title="Laser modules", unique_items=True)
    patch_cords: Optional[List[Patch]] = Field(None, title="Patch cords", unique_items=True)
    light_sources: Optional[
        Annotated[
            List[Union[Laser, LightEmittingDiode]],
            Field(None, title="Light sources", unique_items=True, discriminator="device_type"),
        ]
    ]
    detectors: Optional[List[Detector]] = Field(None, title="Detectors", unique_items=True)
    objectives: Optional[List[Objective]] = Field(None, title="Objectives", unique_items=True)
    filters: Optional[List[Filter]] = Field(None, title="Filters", unique_items=True)
    lenses: Optional[List[Lens]] = Field(None, title="Lenses", unique_items=True)
    digital_micromirror_devices: Optional[List[DigitalMicromirrorDevice]] = Field(None, title="DMDs", unique_items=True)
    polygonal_scanners: Optional[List[PolygonalScanner]] = Field(None, title="Polygonal scanners", unique_items=True)
    pockels_cells: Optional[List[PockelsCell]] = Field(None, title="Pockels cells", unique_items=True)
    additional_devices: Optional[List[Device]] = Field(None, title="Additional devices", unique_items=True)
    calibrations: List[Calibration] = Field(..., title="Full calibration of devices", unique_items=True)
    ccf_coordinate_transform: Optional[str] = Field(
        None,
        title="CCF coordinate transform",
        description="Path to file that details the CCF-to-lab coordinate transform",
    )
    notes: Optional[str] = Field(None, title="Notes")

    @root_validator
    def validate_device_names(cls, values):  # noqa: C901
        """validate that all DAQ channels are connected to devices that
        actually exist
        """

        model_types = [type(model) for model in devices]

        to_check = [field for field in values.keys() if any(isinstance(values.get(field), model) for model in devices)]

        cameras = values.get("cameras")
        ephys_assemblies = values.get("ephys_assemblies")
        laser_assemblies = values.get("laser_assemblies")
        mouse_platform = values.get("mouse_platform")
        daqs = values.get("daqs")



        if daqs is None:
            return values

        device_names = [None]

        for field in to_check:
            if values.get(field) is not None:
                print(values.get(field))
                device_names += [device.name for device in values.get(field)]

        if cameras is not None:
            device_names += [c.camera.name for c in cameras]

        if daqs is not None:
            device_names += [daq.name for daq in daqs]

        if ephys_assemblies is not None:
            device_names += [probe.name for ephys_assembly in ephys_assemblies for probe in ephys_assembly.probes]

        if laser_assemblies is not None:
            device_names += [laser.name for laser_assembly in laser_assemblies for laser in laser_assembly.lasers]

        if mouse_platform is not None:
            device_names += [mouse_platform.name]

        for daq in daqs:
            if daq.channels is not None:
                for channel in daq.channels:
                    if channel.device_name not in device_names:
                        raise ValueError(
                            f"Device name validation error: '{channel.device_name}' "
                            + f"is connected to '{channel.channel_name}' on '{daq.name}', but "
                            + "this device is not part of the rig."
                        )

        return values
