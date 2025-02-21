from .powervle.interface import (PowerVLE, DefaultCallingConvention, PowerVLEBinaryView)
from binaryninja.architecture import Architecture

PowerVLE.register()
# TODO PowerVLE.extend("SP", ...).register()

arch = Architecture[PowerVLE.name]
arch.register_calling_convention(DefaultCallingConvention(arch, 'default'))
arch.standalone_platform.default_calling_convention = arch.calling_conventions['default']