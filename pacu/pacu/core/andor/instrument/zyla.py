from __future__ import absolute_import

from pacu.core.andor.instrument.base import BaseInstrument
from pacu.core.andor.feature.string import StringFeature
from pacu.core.andor.feature.int import IntFeature
from pacu.core.andor.feature.float import FloatFeature
from pacu.core.andor.feature.bool import BoolFeature
from pacu.core.andor.feature.enum import EnumFeature
from pacu.core.andor.feature.base import BaseFeature
from pacu.core.andor.acquisition.zyla import ZylaAcquisition
from pacu.util.prop.memoized import memoized_property

class ZylaInstrument(BaseInstrument):
    camera_model                 = StringFeature('CameraModel')
    controller_id                = StringFeature('ControllerID')
    firmware_version             = StringFeature('FirmwareVersion')
    interface_type               = StringFeature('InterfaceType')
    serial_number                = StringFeature('SerialNumber')
    accumulate_count             = IntFeature('AccumulateCount')
    aoi_height                   = IntFeature('AOIHeight')
    aoi_left                     = IntFeature('AOILeft')
    aoi_stride                   = IntFeature('AOIStride')
    aoi_top                      = IntFeature('AOITop')
    aoi_width                    = IntFeature('AOIWidth')
    baseline                     = IntFeature('Baseline')
    frame_count                  = IntFeature('FrameCount')
    image_size_bytes             = IntFeature('ImageSizeBytes')
    sensor_height                = IntFeature('SensorHeight')
    sensor_width                 = IntFeature('SensorWidth')
    timestamp_clock              = IntFeature('TimestampClock')
    timestamp_clock_freqeuncy    = IntFeature('TimestampClockFrequency')
    bytes_per_pixel              = FloatFeature('BytesPerPixel')
    exposure_time                = FloatFeature('ExposureTime')
    frame_rate                   = FloatFeature('FrameRate')
    max_interface_transfer_rate  = FloatFeature('MaxInterfaceTransferRate')
    pixel_height                 = FloatFeature('PixelHeight') # micrometer
    readout_time                 = FloatFeature('ReadoutTime')
    sensor_temperature           = FloatFeature('SensorTemperature')
    camera_acquiring             = BoolFeature('CameraAcquiring')
    event_enable                 = BoolFeature('EventEnable')
    full_aoi_contol              = BoolFeature('FullAOIControl')
    io_invert                    = BoolFeature('IOInvert')
    metadata_enable              = BoolFeature('MetadataEnable')
    metadata_frame               = BoolFeature('MetadataFrame')
    metadata_timestamp           = BoolFeature('MetadataTimestamp')
    overlap                      = BoolFeature('Overlap')
    sensor_cooling               = BoolFeature('SensorCooling')
    spurious_noise_filter        = BoolFeature('SpuriousNoiseFilter')
    static_blemish_correction    = BoolFeature('StaticBlemishCorrection')
    vertically_centre_aoi        = BoolFeature('VerticallyCentreAOI')
    aoi_binning                  = EnumFeature('AOIBinning')
    auxiliary_out_source         = EnumFeature('AuxiliaryOutSource')
    # aux_out_source_two           = EnumFeature('AuxOutSourceTwo')
    bit_depth                    = EnumFeature('BitDepth')
    cycle_mode                   = EnumFeature('CycleMode')
    electron_shuttering_mode     = EnumFeature('ElectronicShutteringMode')
    event_selector               = EnumFeature('EventSelector')
    fan_speed                    = EnumFeature('FanSpeed')
    io_selector                  = EnumFeature('IOSelector')
    pixel_encoding               = EnumFeature('PixelEncoding')
    pixel_readout_rate           = EnumFeature('PixelReadoutRate')
    simple_preamp_gain_control   = EnumFeature('SimplePreAmpGainControl')
    temperature_status           = EnumFeature('TemperatureStatus')
    trigger_mode                 = EnumFeature('TriggerMode')
    feat_str = StringFeature.descriptor_set()
    feat_int = IntFeature.descriptor_set()
    feat_float = FloatFeature.descriptor_set()
    feat_bool = BoolFeature.descriptor_set()
    feat_enum = EnumFeature.descriptor_set()
    def camera_dump(self):
        return self.handle.command(u'CameraDump')
    def software_trigger(self):
        return self.handle.command(u'SoftwareTrigger')
    def timestamp_clock_reset(self):
        return self.handle.command(u'TimestampClockReset')
    def from_timestamp(self, ts):
        return ts / float(self.timestamp_clock_freqeuncy)
    @property
    def time(self):
        return self.timestamp_clock / self.timestamp_clock_freqeuncy
    acquisition = memoized_property(ZylaAcquisition)
