from .wow_common_types import *
from ..enums.adt_enums import *
from .. import CLIENT_VERSION, WoWVersions

__reload_order_index__ = 2

TILE_SIZE = 5533.333333333
MAP_SIZE_MIN = -17066.66656
MAP_SIZE_MAX = 17066.66657


class OFFSET:
	def __init__(self, file, ofs=0, absolute_adr=0):
		self.ofs = ofs
		self.absolute = absolute_adr
		self.file = file
		self.file._register_offset(self)

	def __del__(self):
		self.file._unregister_offset(self)

	def __int__(self):
		return self.ofs

	def _update(self, distance, address_of_changed):
		if self.absolute > address_of_changed:
			rel_point = self.absolute - self.ofs
			if rel_point <= address_of_changed:
				self.ofs += distance
			self.absolute += distance

	def set(self, ofs, absolute_adr):
		self.ofs = ofs
		self.absolute = absolute_adr

	def set_rel(self, ofs, base):
		self.ofs = ofs
		self.absolute = ofs + base


class ADT_REF:
	def __init__(self, adt):
		self.adt = adt


class MOBILE_CHUNK(ADT_REF):
	def __init__(self, adt):
		ADT_REF.__init__(self, adt)
		self.adt._register_mobile_chunk(self)
		self.address = 0

	def set_address(self, address):
		self.address = address

	def update_address(self, distance, address_of_changed):
		if self.address > address_of_changed:
			self.address += distance


class MVER:
	magic = 'REVM'
	data_size = 4

	def __init__(self):
		self.header = ChunkHeader(MVER.magic, MVER.data_size)
		self.version = 18

	def read(self, f):
		self.header.read(f)
		self.version = uint32.read(f)

		return self

	def write(self, f):
		self.header.write(f)
		uint32.write(f, self.version)

		return self


class MHDR:
	magic = 'RDHM'
	data_size = 54

	def __init__(self, adt):
		self.header = ChunkHeader(MHDR.magic, MHDR.data_size)
		self.start_data = 0
		self.flags = 0
		self.ofs_mcin = OFFSET(adt)
		self.ofs_mtex = OFFSET(adt)
		self.ofs_mmdx = OFFSET(adt)
		self.ofs_mmid = OFFSET(adt)
		self.ofs_mwmo = OFFSET(adt)
		self.ofs_mwid = OFFSET(adt)
		self.ofs_mddf = OFFSET(adt)
		self.ofs_modf = OFFSET(adt)
		self.ofs_mfbo = OFFSET(adt)
		self.ofs_mh2o = OFFSET(adt)
		self.ofs_mtxf = OFFSET(adt)
		self.mamp_value = 0

	def read(self, f):
		self.header.read(f)
		self.start_data = f.tell()
		self.flags = uint32.read(f)
		self.ofs_mcin.set_rel(uint32.read(f), self.start_data)
		self.ofs_mtex.set_rel(uint32.read(f), self.start_data)
		self.ofs_mmdx.set_rel(uint32.read(f), self.start_data)
		self.ofs_mmid.set_rel(uint32.read(f), self.start_data)
		self.ofs_mwmo.set_rel(uint32.read(f), self.start_data)
		self.ofs_mwid.set_rel(uint32.read(f), self.start_data)
		self.ofs_mddf.set_rel(uint32.read(f), self.start_data)
		self.ofs_modf.set_rel(uint32.read(f), self.start_data)
		self.ofs_mfbo.set_rel(uint32.read(f), self.start_data)
		self.ofs_mh2o.set_rel(uint32.read(f), self.start_data)
		self.ofs_mtxf.set_rel(uint32.read(f), self.start_data)
		self.mamp_value = uint8.read(f)

		return self

	def write(self, f):
		self.header.write(f)
		pos = f.tell()
		uint32.write(f, self.flags)
		uint32.write(f, int(self.ofs_mcin))
		uint32.write(f, int(self.ofs_mtex))
		uint32.write(f, int(self.ofs_mmdx))
		uint32.write(f, int(self.ofs_mmid))
		uint32.write(f, int(self.ofs_mwmo))
		uint32.write(f, int(self.ofs_mwid))
		uint32.write(f, int(self.ofs_mddf))
		uint32.write(f, int(self.ofs_modf))
		uint32.write(f, int(self.ofs_mfbo))
		uint32.write(f, int(self.ofs_mh2o))
		uint32.write(f, int(self.ofs_mtxf))
		uint8.write(f, self.mamp_value)

		return self


class MCIN_entry:
	size = 16

	def __init__(self, adt):
		self.offset = OFFSET(adt)
		self.size = 0
		self.flags = 0
		self.async_id = 0

	def read(self, f):
		self.offset.set_rel(uint32.read(f), 0)
		self.size = uint32.read(f)
		self.flags = uint32.read(f)
		self.async_id = uint32.read(f)

		return self

	def write(self, f):
		uint32.write(f, int(self.offset))
		uint32.write(f, self.size)
		uint32.write(f, self.flags)
		uint32.write(f, self.async_id)

		return self



class MCIN(MOBILE_CHUNK):
	magic = 'NICM'
	data_size = 16

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCIN.magic, MCIN.data_size)
		self.entries = [MCIN_entry(adt) for _ in range(256)]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		for entry in self.entries:
			entry.read(f)

		return self

	def write(self, f):
		self.header.size = len(self.entries) * MCIN_entry.size
		self.header.write(f)

		for entry in self.entries:
			entry.write(f)

		return self


class MTEX(MOBILE_CHUNK, StringBlockChunk):
	magic = 'XTEM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		StringBlockChunk.__init__(self)

	def read(self, f):
		self.set_address(f.tell())
		StringBlockChunk.read(self, f)


class MMDX(MOBILE_CHUNK, StringBlockChunk):
	magic = 'XDMM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		StringBlockChunk.__init__(self)
	def read(self, f):
		self.set_address(f.tell())
		StringBlockChunk.read(self, f)


class MMID(MOBILE_CHUNK):
	magic = 'DIMM'
	entry_size = 4

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MMID.magic)
		self.offsets = []

	def _add(self, ofs):
		abs_ofs = ofs + self.adt._get_mmdx_data_start()
		ofs = OFFSET(self.adt, ofs, abs_ofs)
		self.offsets.append(ofs)

	def _remove(self, index):
		del self.offsets[index]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)

		for _ in range(self.header.size // MMID.entry_size):
			ofs = uint32.read(f)
			abs_ofs = ofs + self.adt._get_mmdx_data_start()
			self.offsets.append(OFFSET(self.adt, ofs, abs_ofs))

		return self

	def write(self, f):
		self.header.size = len(self.offsets) * MMID.entry_size
		self.header.write(f)

		for offset in self.offsets:
			uint32.write(f, int(offset))

		return self


class MWMO(MOBILE_CHUNK, StringBlockChunk):
	magic = 'OMWM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		StringBlockChunk.__init__(self)
	def read(self, f):
		self.set_address(f.tell())
		StringBlockChunk.read(self, f)


class MWID(MOBILE_CHUNK):
	magic = 'DIWM'
	entry_size = 4

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MWID.magic)
		self.offsets = []

	def _add(self, ofs):
		abs_ofs = ofs + self.adt._get_mwmo_data_start()
		ofs = OFFSET(self.adt, ofs, abs_ofs)
		self.offsets.append(ofs)

	def _remove(self, index):
		del self.offsets[index]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)

		for _ in range(self.header.size // MWID.entry_size):
			ofs = uint32.read(f)
			abs_ofs = ofs + self.adt._get_mwmo_data_start()
			self.offsets.append(OFFSET(self.adt, ofs, abs_ofs))

	def write(self, f):
		self.header.size = len(self.offsets) * MWID.entry_size
		self.header.write(f)

		for offset in self.offsets:
			uint32.write(f, int(offset))


class ADTDoodadDefinition:
	size = 36

	def __init__(self, name_id=0, unique_id=0, position=None, rotation=None, scale=0, flags=0):
		if position is None:
			position = C3Vector()
		if rotation is None:
			rotation = C3Vector()
		self.name_id = name_id
		self.unique_id = unique_id
		self.position = position
		self.rotation = rotation
		self.scale = scale
		self.flags = flags

	def read(self, f):
		self.name_id = uint32.read(f)
		self.unique_id = uint32.read(f)
		self.position.read(f)
		self.rotation.read(f)
		# self.position = vec3D.read(f)
		# self.rotation = vec3D.read(f)
		self.scale = uint16.read(f)
		self.flags = uint16.read(f)

		return self

	def write(self, f):
		uint32.write(f, self.name_id)
		uint32.write(f, self.unique_id)
		self.position.write(f)
		self.rotation.write(f)
		# vec3D.write(f, self.position)
		# vec3D.write(f, self.rotation)
		uint16.write(f, self.scale)
		uint16.write(f, self.flags)

		return self


class MDDF(MOBILE_CHUNK):
	magic = 'FDDM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MDDF.magic)
		self.doodad_instances = []

	def _add(self, name_id, unique_id, position, rotation, scale, flags):
		if type(position) != C3Vector:
			position = C3Vector(position)
		if type(rotation) != C3Vector:
			rotation = C3Vector(rotation)
		dad = ADTDoodadDefinition(name_id, unique_id, position, rotation, scale, flags)
		self.doodad_instances.append(dad)

	def _remove(self, index):
		del self.doodad_instances[index]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		for _ in range(self.header.size // ADTDoodadDefinition.size):
			self.doodad_instances.append(ADTDoodadDefinition().read(f))

	def write(self, f):
		self.header.size = len(self.doodad_instances) * ADTDoodadDefinition.size
		self.header.write(f)

		for doodad in self.doodad_instances:
			doodad.write(f)


class ADTWMODefinition:
	size = 64

	def __init__(self, name_id=0, unique_id=0, position=None, rotation=None, 
				extents=None, flags=0, doodad_set=0, name_set=0, scale=0):
		if position is None:
			position = C3Vector()
		if rotation is None:
			rotation = C3Vector()
		if extents is None:
			extents = CAaBox()
		self.name_id = name_id
		self.unique_id = unique_id
		self.position = position
		self.rotation = rotation
		self.extents = extents
		self.flags = flags
		self.doodad_set = doodad_set
		self.name_set = name_set
		self.scale = scale

	def read(self, f):
		self.name_id = uint32.read(f)
		self.unique_id = uint32.read(f)
		# self.position = vec3D.read(f)
		# self.rotation = vec3D.read(f)
		self.position.read(f)
		self.rotation.read(f)
		self.extents.read(f)
		self.flags = uint16.read(f)
		self.doodad_set = uint16.read(f)
		self.name_set = uint16.read(f)
		self.scale = uint16.read(f)

	def write(self, f):
		uint32.write(f, self.name_id)
		uint32.write(f, self.unique_id)
		# vec3D.write(f, self.position)
		# vec3D.write(f, self.rotation)
		self.position.write(f)
		self.rotation.write(f)
		self.extents.write(f)
		uint16.write(f, self.flags)
		uint16.write(f, self.doodad_set)
		uint16.write(f, self.name_set)
		uint16.write(f, self.scale)


class MODF(MOBILE_CHUNK):
	magic = 'FDOM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MODF.magic)
		self.wmo_instances = []

	def _add(self, name_id, unique_id, position, rotation, 
			extents, flags, doodad_set, name_set, scale):
		if type(position) != C3Vector:
			position = C3Vector(position)
		if type(rotation) != C3Vector:
			rotation = C3Vector(rotation)
		if type(extents) != CAaBox:
			extents = CAaBox(*extents)
		wmo = ADTWMODefinition(name_id, unique_id, position, rotation, 
			extents, flags, doodad_set, name_set, scale)
		self.wmo_instances.append(wmo)

	def _remove(self, index):
		del self.wmo_instances[index]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		for _ in range(self.header.size // ADTWMODefinition.size):
			wmo_instance = ADTWMODefinition()
			wmo_instance.read(f)
			self.wmo_instances.append(wmo_instance)

	def write(self, f):
		self.header.size = len(self.wmo_instances) * ADTWMODefinition.size
		self.header.write(f)

		for wmo_instance in self.wmo_instances:
			wmo_instance.write(f)


class MFBO(MOBILE_CHUNK):
	magic = 'OBFM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MFBO.magic)
		self.maximum = [[0] * 3] * 3
		self.minimum = [[0] * 3] * 3

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.maximum = [[int16.read(f) for _ in range(3)] for _ in range(3)]
		self.minimum = [[int16.read(f) for _ in range(3)] for _ in range(3)]

	def write(self, f):
		self.header.write(f)
		for r in self.maximum:
			for h in r:
				int16.write(f, h)
		for r in self.minimum:
			for h in r:
				int16.write(f, h)


# class SMLiquidChunk:
#     def __init__(self):
#         self.offset_instances = 0
#         self.layer_count = 0
#         self.offset_attributes = 0

#     def read(self, f):
#         self.offset_instances = uint32.read(f)
#         self.layer_count = uint32.read(f)
#         self.offset_attributes = uint32.read(f)

#     def write(self, f):
#         uint32.write(f, self.offset_instances)
#         uint32.write(f, self.layer_count)
#         uint32.write(f, self.offset_attributes)


# class mh2o_chunk_attributes:
#     def __init__(self):
#         self.fishable = 0
#         self.deep = 0

#     def read(self, f):
#         self.fishable = uint64.read(f)
#         self.deep = uint64.read(f)

#     def write(self, f):
#         uint64.write(f, self.fishable)
#         uint64.write(f, self.deep)


# class MH2O:
#     def __init__(self):
#         self.header = ChunkHeader('O2HM')
#         self.chunks = [SMLiquidChunk() for _ in range(256)]
#         self.liquid_instances = []

#     def read(self, f):
#         self.header.read(f)
#         for chunk in self.chunks:
#             chunk.read()

#     def write(self, f):
class MH2O(MOBILE_CHUNK):
	magic = 'O2HM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MH2O.magic)
		# TODO
		self.data = []

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.data = [uint8.read(f) for _ in range(self.header.size)]

	def write(self, f):
		self.header.size = len(self.data)
		self.header.write(f)
		for c in self.data:
			uint8.write(f, c)


class MTXF(MOBILE_CHUNK):
	magic = 'FXTM'
	entry_size = 4

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MTXF.magic)
		self.flags = []

	def _add(self, flags):
		self.flags.append(flags)
	
	def _remove(self, index):
		del self.flags[index]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		for _ in range(self.header.size // MTXF.entry_size):
			self.flags.append(uint32.read(f))

	def write(self, f):
		self.header.size = len(self.flags) * MTXF.entry_size
		self.header.write()
		for flag in self.flags:
			flag.write(f)


class MCNK(MOBILE_CHUNK):
	magic = 'KNCM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCNK.magic)
		self.flags = 0
		self.index_x = 0
		self.index_y = 0
		self.n_layers = 0
		self.n_doodad_refs = 0

		if CLIENT_VERSION >= WoWVersions.MOP:
			self.hole_high_res = 0
		else:
			self.ofs_mcvt = OFFSET(self.adt)
			self.ofs_mcnr = OFFSET(self.adt)

		self.ofs_mcly = OFFSET(self.adt)
		self.ofs_mcrf = OFFSET(self.adt)
		self.ofs_mcal = OFFSET(self.adt)
		self.size_mcal = 0
		self.ofs_mcsh = OFFSET(self.adt)
		self.size_mcsh = 0
		self.area_id = 0
		self.n_map_obj_refs = 0
		self.holes_low_res = 0
		self.unknown_but_used = 0
		self.low_quality_texture_map = [[0] * 8] * 8
		self.no_effect_doodad = [[0] * 8] * 8
		self.ofs_mcse = OFFSET(self.adt)
		self.n_sound_emitters = 0
		self.ofs_mclq = OFFSET(self.adt)
		self.size_mclq = 0
		self.position = C3Vector()
		self.ofs_mccv = OFFSET(self.adt)
		self.ofs_mclv = OFFSET(self.adt)
		self.unused = 0

		self.mcvt = MCVT(adt)
		self.mcnr = MCNR(adt)
		self.mcly = MCLY(adt, self)
		self.mcrf = MCRF(adt)
		self.mcal = MCAL(adt)
		self.mcsh = MCSH(adt)
		self.mcse = MCSE(adt)
		# self.mclq = MCLQ(adt)    # TODO
		self.mccv = MCCV(adt)
		self.mclv = MCLV(adt)

	def _get_mcal_data_start(self):
		return self.address + int(self.ofs_mcal) + ChunkHeader.size

	def add_sound_emitter(self, entry_id, position, size):
		if position is not C3Vector:
			position = C3Vector(position)
		if size is not C3Vector:
			size = C3Vector(size)
		self.mcse._add_entry(entry_id, position, size)
		self.n_sound_emitters += 1

	def remove_sound_emitter(self, index):
		if index > len(self.mcse.entries) - 1:
			raise IndexError("Index not in entries: {}".format(index))
		
		self.mcse._remove_entry(index)
		self.n_sound_emitters -= 1

	def add_texture_layer(self, texture_id, flags, effect_id, alpha_is_highres):
		if self.n_layers >= 4:
			raise Exception("Chunk already has max texture layers.")

		self.n_layers += 1
		ofs = 0
		adr = 0
		if self.n_layers > 1:
			alpha_is_broken = not (self.flags & ADTChunkFlags.DO_NOT_FIX_ALPHA_MAP)
			alpha_is_compressed = flags & ADTChunkLayerFlags.alpha_map_compressed
			alpha_type = None
			
			if alpha_is_highres:
				if alpha_is_compressed[i]:
					alpha_type = ADTAlphaTypes.HIGHRES_COMPRESSED
				else:
					alpha_type = ADTAlphaTypes.HIGHRES
			else:
				if alpha_is_broken:
					alpha_type = ADTAlphaTypes.BROKEN
				else:
					alpha_type = ADTAlphaTypes.LOWRES
			
			ofs = self.mcal._add_layer(alpha_type)
			adr = ofs + self.mcal.address + ChunkHeader.size
		offset_in_mcal = OFFSET(self.adt, ofs, adr)
		self.mcly._add_layer(texture_id, flags, offset_in_mcal, effect_id)
	
	def remove_texture_layer(self, index):
		if index >= len(self.mcly.layers) or index < 0:
			raise IndexError("Index not in layers: {}".format(index))

		if len(self.mcly.layers) > 1:
			index_in_mcal = index
			if index > 0:
				index_in_mcal -= 1
			
			address = self.mcly.layers[index].offset_in_mcal.absolute
			self.mcal._remove_layer(index_in_mcal, address)

		self.mcly._remove_layer(index)

		if index == 0 and len(self.mcly.layers) > 0:
			self.mcly.layers[0].flags &= ~(ADTChunkLayerFlags.use_alpha_map)
		
		self.n_layers -= 1


	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.flags = uint32.read(f)
		self.index_x = uint32.read(f)
		self.index_y = uint32.read(f)
		self.n_layers = uint32.read(f)
		self.n_doodad_refs = uint32.read(f)

		if CLIENT_VERSION >= WoWVersions.MOP:
			self.hole_high_res = uint64.read(f)
		else:
			self.ofs_mcvt.set_rel(uint32.read(f), self.address)
			self.ofs_mcnr.set_rel(uint32.read(f), self.address)

		self.ofs_mcly.set_rel(uint32.read(f), self.address)
		self.ofs_mcrf.set_rel(uint32.read(f), self.address)
		self.ofs_mcal.set_rel(uint32.read(f), self.address)
		self.size_mcal = uint32.read(f)
		self.ofs_mcsh.set_rel(uint32.read(f), self.address)
		self.size_mcsh = uint32.read(f)
		self.area_id = uint32.read(f)
		self.n_map_obj_refs = uint32.read(f)
		self.holes_low_res = uint16.read(f)
		self.unknown_but_used = uint16.read(f)

		for i in range(8):
			self.low_quality_texture_map[i] = []
			for _ in range(2):
				b = uint8.read(f)
				self.low_quality_texture_map[i] += uint8_to_uint2_list(b)

		for i in range(8):
			b = uint8.read(f)
			self.no_effect_doodad[i] = uint8_to_uint1_list(b)

		self.ofs_mcse.set_rel(uint32.read(f), self.address)
		self.n_sound_emitters = uint32.read(f)
		self.ofs_mclq.set_rel(uint32.read(f), self.address)
		self.size_liquid = uint32.read(f)
		self.position.read(f)
		self.ofs_mccv.set_rel(uint32.read(f), self.address)
		self.ofs_mclv.set_rel(uint32.read(f), self.address)
		self.unused = uint32.read(f)

		f.seek(self.address + int(self.ofs_mcvt))
		self.mcvt.read(f)
		f.seek(self.address + int(self.ofs_mcnr))
		self.mcnr.read(f)
		f.seek(self.address + int(self.ofs_mcly))
		self.mcly.read(f)
		f.seek(self.address + int(self.ofs_mcrf))
		self.mcrf.read(f, self.n_doodad_refs, self.n_map_obj_refs)

		alpha_is_broken = not (self.flags & ADTChunkFlags.DO_NOT_FIX_ALPHA_MAP)
		alpha_is_compressed = []
		for layer in self.mcly.layers:
			is_comp = layer.flags & ADTChunkLayerFlags.alpha_map_compressed
			alpha_is_compressed.append(is_comp)
		f.seek(self.address + int(self.ofs_mcal))
		n_alpha_layers = self.n_layers - 1
		self.mcal.read(f, n_alpha_layers, alpha_is_broken, alpha_is_compressed)

		if (self.flags & ADTChunkFlags.HAS_MCSH):
			f.seek(self.address + int(self.ofs_mcsh))
			self.mcsh.read(f)

		f.seek(self.address + int(self.ofs_mcse))
		self.mcse.read(f, self.n_sound_emitters)

		# TODO: (DEPRECATED)
		# if self.ofs_mclq:
		# 	f.seek(self.start + self.ofs_mclq)
		# 	self.mclq.read(f)

		if (self.flags & ADTChunkFlags.HAS_MCCV):
			f.seek(self.address + int(self.ofs_mccv))
			self.mccv.read(f)

		# TODO
		# f.seek(self.start + self.ofs_mclv)
		# self.mclv.read(f)

	def _set_header_size(self):
		size = 0

		# MCNK header
		size += 128

		# MCVT
		size += ChunkHeader.size
		size += self.mcvt.header.size

		# MCNR
		size += ChunkHeader.size
		size += self.mcnr.header.size
		size += 13		# "unkshit"

		# MCLY
		size += ChunkHeader.size
		for layer in self.mcly.layers:
			size += MCLYLayer.size

		# MCRF
		size += ChunkHeader.size
		for entry in self.mcrf.doodad_refs:
			size += MCRF.entry_size
		for entry in self.mcrf.object_refs:
			size += MCRF.entry_size

		# MCSH
		if self.flags & ADTChunkFlags.HAS_MCSH:
			size += ChunkHeader.size
			size += self.mcsh.header.size

		# MCAL
		size += ChunkHeader.size
		for layer in self.mcal.layers:
			size += layer.size

		# MCSE
		size += ChunkHeader.size
		for entry in self.mcse.entries:
			size += MCSESoundEmitter.size

		# MCCV
		if self.flags & ADTChunkFlags.HAS_MCCV:
			size += ChunkHeader.size
			size += self.mccv.header.size

		self.header.size = size

	def write(self, f):
		self._set_header_size()
		self.header.write(f)
		uint32.write(f, self.flags)
		uint32.write(f, self.index_x)
		uint32.write(f, self.index_y)
		uint32.write(f, self.n_layers)
		uint32.write(f, self.n_doodad_refs)

		if CLIENT_VERSION >= WoWVersions.MOP:
			uint64.write(f, self.hole_high_res)
		else:
			uint32.write(f, int(self.ofs_mcvt))
			uint32.write(f, int(self.ofs_mcnr))

		uint32.write(f, int(self.ofs_mcly))
		uint32.write(f, int(self.ofs_mcrf))
		uint32.write(f, int(self.ofs_mcal))
		uint32.write(f, self.size_mcal)
		uint32.write(f, int(self.ofs_mcsh))
		uint32.write(f, self.size_mcsh)
		uint32.write(f, self.area_id)
		uint32.write(f, self.n_map_obj_refs)
		uint16.write(f, self.holes_low_res)
		uint16.write(f, self.unknown_but_used)

		for i in range(8):
			b = uint2_list_to_uint8(self.low_quality_texture_map[i][0:4])
			uint8.write(f, b)
			b = uint2_list_to_uint8(self.low_quality_texture_map[i][4:])
			uint8.write(f, b)

		for i in range(8):
			b = uint1_list_to_uint8(self.no_effect_doodad[i])
			uint8.write(f, b)

		uint32.write(f, int(self.ofs_mcse))
		uint32.write(f, self.n_sound_emitters)
		uint32.write(f, int(self.ofs_mclq))
		uint32.write(f, self.size_liquid)
		self.position.write(f)
		uint32.write(f, int(self.ofs_mccv))
		uint32.write(f, int(self.ofs_mclv))
		uint32.write(f, self.unused)

		f.seek(self.address + int(self.ofs_mcvt))
		self.mcvt.write(f)
		f.seek(self.address + int(self.ofs_mcnr))
		self.mcnr.write(f)
		f.seek(self.address + int(self.ofs_mcly))
		self.mcly.write(f)
		f.seek(self.address + int(self.ofs_mcrf))
		self.mcrf.write(f)

		f.seek(self.address + int(self.ofs_mcal))
		self.mcal.write(f)

		if (self.flags & ADTChunkFlags.HAS_MCSH):
			f.seek(self.address + int(self.ofs_mcsh))
			self.mcsh.write(f)

		f.seek(self.address + int(self.ofs_mcse))
		self.mcse.write(f)

		# if self.ofs_mclq:
		# 	f.seek(self.start + self.ofs_mclq)
		# 	self.mclq.read(f)

		if (self.flags & ADTChunkFlags.HAS_MCCV):
			f.seek(self.address + int(self.ofs_mccv))
			self.mccv.write(f)

		# f.seek(self.start + self.ofs_mclv)
		# self.mclv.read(f)


class MCVT(MOBILE_CHUNK):
	magic = 'TVCM'
	data_size = 580

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCVT.magic, MCVT.data_size)
		self.height = [0.0] * 145

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.height = [float32.read(f) for _ in range(145)]

	def write(self, f):
		self.header.write(f)
		for value in self.height: float32.write(f, value)


class MCLV(MOBILE_CHUNK):
	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader('VLCM', 580)
		self.colors = [(255, 255, 255, 255)] * 145

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.colors = [uint8.read(f, 4) for _ in range(145)]

	def write(self, f):
		self.header.write(f)
		for value in self.colors: uint8.write(f, value, 4)


class MCCV(MOBILE_CHUNK):
	magic = 'VCCM'
	data_size = 580

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCCV.magic, MCCV.data_size)
		self.colors = [(255, 255, 255, 255)] * 145

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.colors = [uint8.read(f, 4) for _ in range(145)]

	def write(self, f):
		self.header.write(f)
		for value in self.colors: uint8.write(f, value, 4)


class MCNR(MOBILE_CHUNK):
	magic = 'RNCM'
	data_size = 435 if CLIENT_VERSION <= WoWVersions.WOTLK else 448

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCNR.magic, MCNR.data_size)
		self.normals = [(0, 0, 0)] * 145
		self.unknown = [0] * 13

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		self.normals = [int8.read(f, 3) for _ in range(145)]
		self.unknown = uint8.read(f, 13)

	def write(self, f):
		self.header.write(f)
		for normal in self.normals: int8.write(f, normal, 3)
		for unk in self.unknown: uint8.write(f, unk)


class MCLYLayer:
	size = 16

	def __init__(self, adt, chunk, texture_id=0, flags=0, offset_in_mcal=None, effect_id=0):
		if offset_in_mcal is None:
			offset_in_mcal = OFFSET(adt)
		self.chunk = chunk
		self.texture_id = texture_id
		self.flags = flags
		self.offset_in_mcal = offset_in_mcal
		self.effect_id = effect_id

	def read(self, f):
		self.texture_id = uint32.read(f)
		self.flags = uint32.read(f)

		mcal_data_start = self.chunk._get_mcal_data_start()
		self.offset_in_mcal.set_rel(uint32.read(f), mcal_data_start)
		self.effect_id = uint32.read(f)

	def write(self, f):
		uint32.write(f, self.texture_id)
		uint32.write(f, self.flags)
		uint32.write(f, int(self.offset_in_mcal))
		uint32.write(f, self.effect_id)


class MCLY(MOBILE_CHUNK):
	magic = 'YLCM'

	def __init__(self, adt, chunk):
		MOBILE_CHUNK.__init__(self, adt)
		self.chunk = chunk
		self.header = ChunkHeader(MCLY.magic)
		self.layers = []

	def _add_layer(self, texture_id, flags, offset_in_mcal, effect_id):
		layer = MCLYLayer(self.adt, self.chunk, texture_id, flags, offset_in_mcal, effect_id)
		self.layers.append(layer)
		self.adt._size_changed(MCLYLayer.size, self.address)

	def _remove_layer(self, index):
		del self.layers[index]
		self.adt._size_changed(-MCLYLayer.size, self.address)

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)

		for _ in range(self.header.size // MCLYLayer.size):
			layer = MCLYLayer(self.adt, self.chunk)
			layer.read(f)
			self.layers.append(layer)

	def write(self, f):
		self.header.size = len(self.layers) * MCLYLayer.size
		self.header.write(f)

		for layer in self.layers:
			layer.write(f)


class MCRF(MOBILE_CHUNK):
	magic = 'MCRF'
	entry_size = 4

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCRF.magic)
		self.doodad_refs = []
		self.object_refs = []

	def _add_doodad(self, index_in_mddf):
		self.doodad_refs.append(index_in_mddf)

	def _remove_doodad(self, index_in_mddf):
		self.doodad_refs.remove(index_in_mddf)
		for i in range(len(self.doodad_refs)):
			if self.doodad_refs[i] > index_in_mddf:
				self.doodad_refs[i] -= 1

	def _add_object(self, index_in_modf):
		self.object_refs.append(index_in_modf)

	def _remove_object(self, index_in_modf):
		self.object_refs.remove(index_in_modf)
		for i in range(len(self.object_refs)):
			if self.object_refs[i] > index_in_modf:
				self.object_refs[i] -= 1

	def read(self, f, n_doodad_refs, n_object_refs):
		self.set_address(f.tell())
		self.header.read(f)
		self.doodad_refs = [uint32.read(f) for _ in range(n_doodad_refs)]
		self.object_refs = [uint32.read(f) for _ in range(n_object_refs)]

	def write(self, f):
		n_doodad_refs = len(self.doodad_refs)
		n_object_refs = len(self.object_refs)
		self.header.size = n_doodad_refs * MCRF.entry_size + n_object_refs * MCRF.entry_size
		self.header.write(f)

		if n_doodad_refs > 0:
			uint32.write(f, self.doodad_refs, n_doodad_refs)
		if n_object_refs > 0:
			uint32.write(f, self.object_refs, n_object_refs)

class MCSH(MOBILE_CHUNK):
	magic = 'HSCM'
	data_size = 512
	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCSH.magic, MCSH.data_size)
		self.shadow_map = [[0 for _ in range(64)] for _ in range(64)]

	def read(self, f):
		self.set_address(f.tell())
		self.header.read(f)
		shadow_map_flat = []
		for i in range(512):
			b = uint8.read(f)
			shadow_map_flat += uint8_to_uint1_list(b)
		self.shadow_map = [[shadow_map_flat[i * 64 + j] for j in range(64)] for i in range(64)]

	def write(self, f):
		self.header.write(f)
		for i in range(64):
			for j in range(0, 64, 8):
				b = uint1_list_to_uint8(self.shadow_map[i][j:j+8])
				uint8.write(f, b)


class MCALLayer:
	def __init__(self, type=None):
		self.type = type
		self.alpha_map = [[0 for _ in range(64)] for _ in range(64)]

	def _set_class(self):
		class_map = {
			ADTAlphaTypes.LOWRES : MCALLayerLowresOrBroken,
			ADTAlphaTypes.BROKEN : MCALLayerLowresOrBroken,
			ADTAlphaTypes.HIGHRES : MCALLayerHighres,
			ADTAlphaTypes.HIGHRES_COMPRESSED : MCALLayerHighresCompressed,
		}
		self.__class__ = class_map[self.type]

	def is_fully_transparent(self):
		flattened = [item for sublist in self.alpha_map for item in sublist]
		return not any(flattened)
			
	def read(self, f, alpha_type):
		self.type = alpha_type
		self._set_class()
		self.read(f)

	# write handled in subclasses


class MCALLayerLowresOrBroken(MCALLayer):
	size = ADTAlphaSize.LOWRES

	def read(self, f):
		cur_pos = 0
		alpha_map_flat = [0] * ADTAlphaSize.HIGHRES

		for i in range(ADTAlphaSize.LOWRES):
			cur_byte = uint8.read(f)

			nibble1 = cur_byte & 0x0F
			nibble2 = (cur_byte & 0xF0) >> 4

			first = nibble1 * 255 // 15
			second = nibble2 * 255 // 15

			alpha_map_flat[i + cur_pos + 0] = first
			alpha_map_flat[i + cur_pos + 1] = second
			cur_pos += 1

		# Nice cropcircles
		# self.alpha_map = [[alpha_map_flat[i * j] for i in range(64)] for j in range(64)]
		self.alpha_map = [[alpha_map_flat[i * 64 + j] for j in range(64)] for i in range(64)]

		if self.type == ADTAlphaTypes.BROKEN:
			for row in self.alpha_map:
				row[63] = row[62]

			for i, column in enumerate(self.alpha_map[62]):
				self.alpha_map[63][i] = column

	def write(self, f):
		alpha_map_flat = []
		for row in self.alpha_map:
			for value in row:
				alpha_map_flat.append(value)

		for i in range(0, ADTAlphaSize.HIGHRES, 2):
			nibble1 = alpha_map_flat[i] // (255 // 15)
			nibble2 = alpha_map_flat[i + 1] // (255 // 15)
			uint8.write(f, nibble1 + (nibble2 << 4))


class MCALLayerHighres(MCALLayer):
	size = ADTAlphaSize.HIGHRES

	def read(self, f):
		self.alpha_map = [[uint8.read(f) for _ in range(64)] for _ in range(64)]

	def write(self, f):
		for row in self.alpha_map:
			for value in row:
				uint8.write(f, value)


class MCALLayerHighresCompressed(MCALLayer):
	size = ADTAlphaSize.HIGHRES
	
	def read(self, f):
		alpha_map_flat = [0] * ADTAlphaSize.HIGHRES
		alpha_offset = 0

		while alpha_offset < ADTAlphaSize.HIGHRES:
			cur_byte = uint8.read(f)
			mode = bool(cur_byte >> 7)
			count = cur_byte & 0b1111111

			if mode:  # fill
				alpha = uint8.read(f)
				for i in range(count):
					alpha_map_flat[alpha_offset] = alpha
					alpha_offset += 1
			else:  # copy
				for i in range(count):
					alpha_map_flat[alpha_offset] = uint8.read(f)
					alpha_offset += 1

	def write(self, f):
		alpha_map_flat = []
		for row in self.alpha_map:
			for value in row:
				alpha_map_flat.append(value)

		class Cache:
			def __init__(self, pos=0, val=256):
				self.reset_pos(pos)
				self.reset_val(val)

			def reset_pos(self, pos):
				self.pos = pos
				self.stride = 1

			def reset_val(self, val):
				self.val = val
				self.count = 1

			def dump(self, file, mode=None, container=None):
				mode = mode if mode is not None else self.count > 1

				if not (mode or container):
					return False

				count = (self.count if mode else self.stride - 1) & 0x7F
				uint8.write(file, mode * 0x80 | count)

				if mode:
					uint8.write(file, self.val)
				else:
					for j in range(self.pos, self.pos + count):
						uint8.write(file, container[j])

				return True

		cache = Cache(0, alpha_map_flat[0])

		for pos, val in enumerate(alpha_map_flat, 1):
			if not (pos % 64):
				cache.dump(f, container=alpha_map_flat)
				cache.reset_pos(pos)
				cache.reset_val(val)
				continue

			if cache.val != val:
				if cache.count > 1:
					cache.dump(f, True)
					cache.reset_pos(pos)
				else:
					cache.stride += 1

				cache.reset_val(val)
			else:
				if cache.count == 1 and cache.stride > 1:
					cache.dump(f, False, alpha_map_flat)

				cache.count += 1

		cache.dump(f, container=alpha_map_flat)


class MCAL(MOBILE_CHUNK):
	magic = 'LACM'

	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCAL.magic)
		self.layers = []

	def _add_layer(self, type):
		layer = MCALLayer(type)
		layer._set_class()
		self.layers.append(layer)
		ofs = 0
		for i in range(1, len(self.layers)):
			ofs += self.layers[i].size

		address_of_change = self.address + ChunkHeader.size + ofs
		self.adt._size_changed(layer.size, address_of_change)
		return ofs

	def _remove_layer(self, index, address):
		self.adt._size_changed(-self.layers[index].size, address)
		del self.layers[index]

	def _get_alpha_type(self, alpha_is_highres, alpha_is_compressed, alpha_is_broken):
		alpha_type = None

		if alpha_is_highres:
			if alpha_is_compressed:
				alpha_type = ADTAlphaTypes.HIGHRES_COMPRESSED
			else:
				alpha_type = ADTAlphaTypes.HIGHRES
		else:
			if alpha_is_broken:
				alpha_type = ADTAlphaTypes.BROKEN
			else:
				alpha_type = ADTAlphaTypes.LOWRES

		return alpha_type

	def read(self, f, n_alpha_layers, alpha_is_broken, alpha_is_compressed):
		self.set_address(f.tell())
		self.header.read(f)

		if n_alpha_layers < 1:
			return

		alpha_is_highres = self.adt.highres
		for i in range(n_alpha_layers):
			layer = MCALLayer()
			alpha_type = self._get_alpha_type(alpha_is_highres, alpha_is_compressed[i], alpha_is_broken)
			layer.read(f, alpha_type)
			self.layers.append(layer)

	def write(self, f):
		size = 0
		for layer in self.layers:
			size += layer.size
		self.header.size = size
		self.header.write(f)
		for layer in self.layers:
			layer.write(f)


class MCSESoundEmitter:
	size = 28

	def __init__(self, entry_id=0, position=None, size=None):
		if position is None:
			position = C3Vector()
		if size is None:
			size = C3Vector()
		self.entry_id = entry_id
		self.position = position
		self.size = size

	def read(self, f):
		self.entry_id = uint32.read(f)
		self.position.read(f)
		self.size.read(f)

	def write(self, f):
		uint32.write(f, self.entry_id)
		self.position.write(f)
		self.size.write(f)


class MCSE(MOBILE_CHUNK):
	magic = 'ESCM'
	
	def __init__(self, adt):
		MOBILE_CHUNK.__init__(self, adt)
		self.header = ChunkHeader(MCSE.magic)
		self.entries = []

	def _add_entry(self, entry_id, position, size):
		entry = MCSESoundEmitter(entry_id, position, size)
		self.entries.append(entry)
		self.adt._size_changed(MCSESoundEmitter.size, self.address)

	def _remove_entry(self, index):
		del self.entries[index]
		self.adt._size_changed(-MCSESoundEmitter.size, self.address)

	def read(self, f, n_sound_emitters):
		self.set_address(f.tell())
		self.header.read(f)
		self.entries = [MCSESoundEmitter() for _ in range(n_sound_emitters)]

	def write(self, f):
		self.header.size = len(self.entries) * MCSESoundEmitter.size
		self.header.write(f)
		for entry in self.entries:
			entry.write(f)


# TODO
# class MCLQ:
	# def __init__(self):
	# def read(self, f):
	# def write(self, f):



def uint8_to_uintX_list(uint8, bit_depth=1, LSB_first=True):
	l = []
	mask = 0b1

	for _ in range(bit_depth - 1):
		mask = (mask << 1) | 0b1

	for i in range(0, 8, bit_depth):
		n = None
		if LSB_first:
			n = (uint8 >> i) & mask
		else:
			n = (uint8 >> (8-i-bit_depth)) & mask
		l.append(n)

	return l

def uint8_to_uint1_list(uint8, LSB_first=True):
	return uint8_to_uintX_list(uint8, 1)
def uint8_to_uint2_list(uint8, LSB_first=True):
	return uint8_to_uintX_list(uint8, 2)


def smaller_list_to_uint8(l, bit_depth=1, LSB_first=True):
	if (len(l) * bit_depth) != 8:
		raise ValueError('List length * bit depth should equal 8.')

	uint8 = 0
	for i in range(len(l)):
		if LSB_first:
			uint8 |= l[i] << (bit_depth * i)
		else:
			uint8 |= l[-1 - i] << (bit_depth * i)

	return uint8

def uint1_list_to_uint8(l, LSB_first=True):
	return smaller_list_to_uint8(l, 1, LSB_first)
def uint2_list_to_uint8(l, LSB_first=True):
	return smaller_list_to_uint8(l, 2, LSB_first)