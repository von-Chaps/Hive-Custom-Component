"""Support for the Hive sensors."""
from datetime import timedelta

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import TEMP_CELSIUS, POWER_WATT, PERCENTAGE
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import HiveEntity
from .const import DOMAIN

PARALLEL_UPDATES = 0
SCAN_INTERVAL = timedelta(seconds=15)
DEVICETYPE = {
    "Battery": {"icon": "mdi:battery", "unit": PERCENTAGE, "type": SensorDeviceClass.BATTERY},
    "Heating_Current_Temperature": {"icon": "mdi:thermometer", "unit": TEMP_CELSIUS, "type": SensorDeviceClass.TEMPERATURE},
    "Heating_Target_Temperature": {"icon": "mdi:thermometer", "unit": TEMP_CELSIUS, "type": SensorDeviceClass.TEMPERATURE},
    "Heating_State": {"icon": "mdi:radiator"},
    "Heating_Mode": {"icon": "mdi:radiator"},
    "Heating_Boost": {"icon": "mdi:radiator"},
    "Mode": {"icon": "mdi:eye"},
    "Availability": {"icon": "mdi:check-circle"},
    "Power": {"unit": POWER_WATT, "type": SensorDeviceClass.POWER},
}


async def async_setup_entry(
    hass: HomeAssistant, entry: ConfigEntry, async_add_entities: AddEntitiesCallback
) -> None:
    """Set up Hive thermostat based on a config entry."""

    hive = hass.data[DOMAIN][entry.entry_id]
    devices = hive.session.deviceList.get("sensor")
    entities = []
    if devices:
        for dev in devices:
            entities.append(HiveSensorEntity(hive, dev))
    async_add_entities(entities, True)


class HiveSensorEntity(HiveEntity, SensorEntity):
    """Hive Sensor Entity."""

    @property
    def unique_id(self):
        """Return unique ID of entity."""
        return self._unique_id

    @property
    def device_info(self) -> DeviceInfo:
        """Return device information."""
        return DeviceInfo(
            identifiers={(DOMAIN, self.device["device_id"])},
            manufacturer=self.device["deviceData"]["manufacturer"],
            model=self.device["deviceData"]["model"],
            name=self.device["device_name"],
            sw_version=self.device["deviceData"]["version"],
            via_device=(DOMAIN, self.device["parentDevice"]),
        )

    @property
    def available(self):
        """Return if sensor is available."""
        return self.device.get("deviceData", {}).get("online")

    @property
    def device_class(self):
        """Device class of the entity."""
        return DEVICETYPE[self.device["hiveType"]].get("type", "None")

    @property
    def native_unit_of_measurement(self):
        """Return the unit of measurement."""
        return DEVICETYPE[self.device["hiveType"]].get("unit")

    @property
    def name(self):
        """Return the name of the sensor."""
        return self.device["haName"]

    @property
    def native_value(self):
        """Return the state of the sensor."""
        return self.device["status"]["state"]

    async def async_update(self):
        """Update all Node data from Hive."""
        await self.hive.session.updateData(self.device)
        self.device = await self.hive.sensor.getSensor(self.device)
