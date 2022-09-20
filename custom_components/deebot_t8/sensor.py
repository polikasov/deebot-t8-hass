from ast import Sub
from typing import Optional

from deebot_t8 import DeebotEntity

from homeassistant.components.sensor import SensorEntity
from homeassistant.components.camera import Camera
from homeassistant.config_entries import ConfigEntry
from . import DataEntry
from .mappainter import MapPainter
from .const import (
    DOMAIN, CLEAN_TYPE_MAP, WATER_LEVEL_NAME_MAP, FAN_SPEED_NAME_MAP)
from .subscribed_entity_mixin import SubscribedEntityMixin
import time

ATTR_GENERATED_AT = "generated_at"

async def async_setup_entry(hass, config_entry: ConfigEntry,
                            async_add_entities):
    """Add switches for passed config_entry in HA."""
    entry_data: DataEntry = hass.data[DOMAIN][config_entry.entry_id]
    to_add = []
    mapper = MapPainter()
    
    for entity in entry_data.entities:
        to_add.extend([
            DeebotGenericSensor(
                entity,
                'Area Cleaned Total',
                "m²",
                'mdi:shape-square-plus',
                lambda: entity.state.total_stats.area if entity.state.total_stats is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Cleaning Time Total',
                'hours',
                'mdi:timer',
                lambda: round(entity.state.total_stats.time / 60 / 60,
                              1) if entity.state.total_stats is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Num Cleans Total',
                'cleanings',
                'mdi:counter',
                lambda: entity.state.total_stats.count if entity.state.total_stats is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Current Clean Type',
                None,
                'mdi:broom',
                lambda: CLEAN_TYPE_MAP.get(entity.state.clean_type),
            ),
            DeebotGenericSensor(
                entity,
                'Area Cleaned',
                "m²",
                'mdi:shape-square-plus',
                lambda: entity.state.clean_stats.area if entity.state.clean_stats is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Cleaning Time',
                "minutes",
                'mdi:timer',
                lambda: round(entity.state.clean_stats.time / 60,
                              1) if entity.state.clean_stats is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Avoid Count',
                "avoidances",
                'mdi:undo-variant',
                lambda: entity.state.clean_stats.avoid_count if entity.state.clean_stats and entity.state.clean_stats.avoid_count is not None else None,
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Fan Speed',
                None,
                'mdi:weather-windy',
                lambda: FAN_SPEED_NAME_MAP.get(entity.state.vacuum_speed),
                False,
            ),
            DeebotGenericSensor(
                entity,
                'Water Level',
                None,
                'mdi:water',
                lambda: WATER_LEVEL_NAME_MAP.get(entity.state.water_level),
            ),
            DeebotGenericSensor(
                entity,
                'Main Brush',
                '%',
                'mdi:broom',
                lambda: round(entity.state.lifespan.get('brush').left / entity.state.lifespan.get('brush').total *
                              100, 1) if entity.state.lifespan is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Side Brush',
                '%',
                'mdi:broom',
                lambda: round(entity.state.lifespan.get('sideBrush').left / entity.state.lifespan.get('sideBrush').total *
                              100, 1) if entity.state.lifespan is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Filter',
                '%',
                'mdi:filter',
                lambda: round(entity.state.lifespan.get('heap').left / entity.state.lifespan.get('heap').total *
                              100, 1) if entity.state.lifespan is not None else None,
            ),
            DeebotGenericSensor(
                entity,
                'Unit Care',
                '%',
                'mdi:hand-heart',
                lambda: round(entity.state.lifespan.get('unitCare').left / entity.state.lifespan.get('unitCare').total *
                              100, 1) if entity.state.lifespan is not None else None,
            ),
            DeebotGenericCamera(
                name = "RobotX Camera",
                painter = mapper,
                mapUpdater = lambda: mapper.add(x=entity.state.position.get('x'), y=entity.state.position.get('y')) if entity.state.position is not None else None
            )
        ])

    async_add_entities(to_add)
    return True

class DeebotGenericCamera(Camera):
    """Deebot cleaning map for last clean."""

    def __init__(
        self, name = "Default Camera", painter = None, mapUpdater = None) -> None:
        """Initialize Yeedi cleaning map."""
        super().__init__()
        # self._mapdata = mapdata
        self._available = None
        self._generated_at = 0
        self._lastPosSupdate = 0
        self._image: bytes | None = None
        self._imageURL: str | None = None
        self._imagePath: str | None = None
        self.mapupdater = mapUpdater
        self.paint = painter

    def camera_image(
        self, width: int | None = None, height: int | None = None
    ) -> bytes | None:
        """Return image response."""
        self.update()
        return self._image

    def update(self) -> None:
        """Check the contents of the map list."""

        if time.time() - self._lastPosSupdate > 3:
            self.mapUpdater()
            self._lastPosSupdate = time.time()

        if time.time() - self._generated_at < 15:
            return 0
        self._generated_at = time.time()
        self.paint.paint()
        self._image = open(self.paint.getCurFileName())
        self._imagePath = self.paint.getCurFileName()
        self._imageURL = self.paint.getFilePath()
        self._available = True

    @property
    def name(self) -> str:
        """Return the name of this camera."""
        return self._attr_name

    @property
    def unique_id(self) -> str:
        """Return unique ID."""
        return "RobotX_Camera"

    @property
    def available(self) -> bool:
        """Return if the robot is available."""
        return self._available

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return the state attributes of the vacuum cleaner."""
        data: dict[str, Any] = {}

        if self._generated_at is not None:
            data[ATTR_GENERATED_AT] = self._generated_at
        if self._imagePath is not None:
            data["image_path"] =  self._imagePath
        if self._imageURL is not None:
            data["image_url"] = self._imageURL
        return 
    

class DeebotGenericSensor(SubscribedEntityMixin, SensorEntity):
    def __init__(
            self, api_entity: DeebotEntity, attr_name: str,
            unit_of_measurement: Optional[str], icon: str,
            getter, enabled_by_default: bool = True):
        self.api_entity = api_entity
        self.attr_name = attr_name
        self.getter = getter

        self._attr_icon = icon
        self._attr_unit_of_measurement = unit_of_measurement
        self._attr_entity_registry_enabled_default = enabled_by_default

    @property
    def unique_id(self) -> str:
        return self.api_entity._device.id + '_' + self.attr_name

    @property
    def name(self) -> str:
        return self.api_entity._device.name + ' ' + self.attr_name

    @property
    def state(self):
        return self.getter()
