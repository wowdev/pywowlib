from .file_formats.adt_chunks import *
from .file_formats.wow_common_types import ChunkHeader
from .enums.adt_enums import *
from io import BufferedReader

__reload_order_index__ = 3


class ADTFile:
	# def __init__(self, version, filepath=None):
	def __init__(self, filepath=None, highres=True):

		self.filepath = filepath
		self._mobile_chunks = []
		self._offsets = []

		# TODO: read from WDT MPHD flags if available?
		self.highres = highres

		# initialize chunks
		self.mver = MVER()
		self.mhdr = MHDR(self)
		self.mcin = MCIN(self)
		self.mtex = MTEX(self)
		self.mmdx = MMDX(self)
		self.mmid = MMID(self)
		self.mwmo = MWMO(self)
		self.mwid = MWID(self)
		self.mddf = MDDF(self)
		self.modf = MODF(self)
		self.mfbo = MFBO(self)
		self.mh2o = MH2O(self)
		self.mtxf = MTXF(self)
		self.mcnk = [[MCNK(self) for _ in range(16)] for _ in range(16)]

		if self.filepath:
			with open(self.filepath, 'rb') as f:
				self.read(f)

	def _register_mobile_chunk(self, chunk):
		self._mobile_chunks.append(chunk)

	def _update_mobile_chunks(self, distance, address_of_changed):
		for chunk in self._mobile_chunks:
			chunk.update_address(distance, address_of_changed)

	def _register_offset(self, ofs):
		self._offsets.append(ofs)

	def _unregister_offset(self, ofs):
		self._offsets.remove(ofs)

	def _update_offsets(self, distance, address_of_changed):
		for ofs in self._offsets:
			ofs._update(distance, address_of_changed)

	def _get_mmdx_data_start(self):
		return self.mmdx.address + ChunkHeader.size

	def _get_mwmo_data_start(self):
		return self.mwmo.address + ChunkHeader.size

	def add_texture_filename(self, filename, mtxf_flags=0):
		try:
			return self.mtex.filenames.index(filename)
		except:	# Python, more like Fuckoff
			pass
		
		self.mtex.filenames._add(filename)
		size = len(filename) + 1
		self._size_changed(size, self.mtex.address)

		if int(self.mhdr.ofs_mtxf):
			self.mtxf._add(mtxf_flags)
			self._size_changed(MTXF.entry_size, self.mtxf.address)
		
		return len(self.mtex.filenames) - 1

	def replace_texture_filename(self, index, new_filename):
		if index > len(self.mtex.filenames) - 1:
			raise IndexError("Index not in filenames: {}".format(index))
		
		old_size = len(self.mtex.filenames[index])
		new_size = len(new_filename)
		self.mtex.filenames._replace(index, new_filename)
		size_change = new_size - old_size
		if size_change:
			self._size_changed(size_change, self.mtex.address)

	def remove_texture_filename(self, index):
		# TODO: what do we do with MCLY entries that ref this?
		if index > len(self.mtex.filenames) - 1:
			raise IndexError("Index not in filenames: {}".format(index))
		
		size_change = -(len(self.mtex.filenames[index]) + 1)
		self.mtex.filenames._remove(index)
		self._size_changed(size_change, self.mtex.address)

		if int(self.mhdr.ofs_mtxf):
			self.mtxf._remove(index)
			self._size_changed(-MTXF.entry_size, self.mtxf.address)

	def _add_model_filename(self, filename, filename_chunk, offset_chunk):
		try:
			return filename_chunk.filenames.index(filename)
		except:
			pass

		ofs_in_fc = filename_chunk.filenames.size
		# Dirty, but should be safe:
		address_of_changed = filename_chunk.address + filename_chunk.filenames.size + ChunkHeader.size - 1
		filename_chunk.filenames._add(filename)
		distance = len(filename) + 1
		self._size_changed(distance, address_of_changed)
		offset_chunk._add(ofs_in_fc)
		self._size_changed(offset_chunk.entry_size, offset_chunk.address)

		return len(filename_chunk.filenames) - 1

	def _replace_model_filename(self, index, new_filename, filename_chunk, offset_chunk):
		if index > len(filename_chunk.filenames) - 1:
			raise IndexError("Index not in filenames: {}".format(index))
		
		address_of_changed = offset_chunk.offsets[index].absolute
		old_size = len(filename_chunk.filenames[index])
		new_size = len(new_filename)
		filename_chunk.filenames._replace(index, new_filename)
		distance = new_size - old_size
		if distance:
			self._size_changed(distance, address_of_changed)

	def _remove_model_filename(self, index, filename_chunk, offset_chunk):
		if index > len(filename_chunk.filenames) - 1:
			raise IndexError("Index not in filenames: {}".format(index))
		
		address_of_changed = offset_chunk.offsets[index].absolute
		distance = -(len(filename_chunk.filenames[index]) + 1)
		filename_chunk.filenames._remove(index)
		self._size_changed(distance, address_of_changed)

		offset_chunk._remove(index)
		address_of_changed = offset_chunk.address
		distance = -offset_chunk.entry_size
		self._size_changed(distance, address_of_changed)
	
	def add_m2_filename(self, filename):
		return self._add_model_filename(filename, self.mmdx, self.mmid)
	def replace_m2_filename(self, index, new_filename):
		self._replace_model_filename(index, new_filename, self.mmdx, self.mmid)
	def remove_m2_filename(self, index):
		self._remove_model_filename(index, self.mmdx, self.mmid)

	def add_wmo_filename(self, filename):
		self._add_model_filename(filename, self.mwmo, self.mwid)
	def replace_wmo_filename(self, index, new_filename):
		self._replace_model_filename(index, new_filename, self.mwmo, self.mwid)
	def remove_wmo_filename(self, index):
		self._remove_model_filename(index, self.mwmo, self.mwid)


	def add_m2_instance(self, which_chunks, name_id, unique_id, position, rotation, scale, flags):
		self.mddf._add(name_id, unique_id, position, rotation, scale, flags)
		distance = ADTDoodadDefinition.size
		self._size_changed(distance, self.mddf.address)

		for row, col in which_chunks:	# list of tuples [(row, col), (row, col), etc]
			mddf_index = len(self.mddf.doodad_instances) - 1
			self.mcnk[row][col].mcrf._add_doodad(mddf_index)
			self._size_changed(MCRF.entry_size, self.mcnk[row][col].mcrf.address)
			self.mcnk[row][col].n_doodad_refs += 1
		# TODO: sort MCRF doodad_refs by size category		

	def remove_m2_instance(self, index):
		if index > len(self.mddf.doodad_instances) - 1:
			raise IndexError("Index not in doodad_instances: {}".format(index))

		self.mddf._remove(index)
		distance = -ADTDoodadDefinition.size
		self._size_changed(distance, self.mddf.address)

		for row in range(16):
			for col in range(16):
				chunk = self.mcnk[row][col]
				if index in chunk.mcrf.doodad_refs:
					chunk.mcrf._remove_doodad(index)
					self._size_changed(-MCRF.entry_size, chunk.mcrf.address)
					chunk.n_doodad_refs -= 1

	
	def add_wmo_instance(self, which_chunks, name_id, unique_id, position, rotation, 
						extents, flags, doodad_set, name_set, scale):
		self.modf._add(name_id, unique_id, position, rotation, 
						extents, flags, doodad_set, name_set, scale)
		distance = ADTWMODefinition.size
		self._size_changed(distance, self.modf.address)

		for row, col in which_chunks:	# list of tuples [(row, col), (row, col), etc]
			modf_index = len(self.modf.wmo_instances) - 1
			self.mcnk[row][col].mcrf._add_object(modf_index)
			self._size_changed(MCRF.entry_size, self.mcnk[row][col].mcrf.address)
			self.mcnk[row][col].n_map_obj_refs += 1

	def remove_wmo_instance(self, index):
		if index > len(self.modf.wmo_instances) - 1:
			raise IndexError("Index not in wmo_instances: {}".format(index))

		self.modf._remove(index)
		distance = -ADTWMODefinition.size
		self._size_changed(distance, self.modf.address)

		for row in range(16):
			for col in range(16):
				chunk = self.mcnk[row][col]
				if index in chunk.mcrf.object_refs:
					chunk.mcrf._remove_object(index)
					self._size_changed(-MCRF.entry_size, chunk.mcrf.address)
					chunk.n_map_obj_refs -= 1


	# Call this whenever the size of something changes to update offsets.
	def _size_changed(self, distance, address_of_changed):
		self._update_offsets(distance, address_of_changed)
		self._update_mobile_chunks(distance, address_of_changed)


	def read(self, f):
		self.mver.read(f)
		if self.mver.version != 18:  # Blizzard has never cared to change it so far
			raise NotImplementedError('Unknown ADT version: ({})'.format(self.mver.version))

		self.mhdr.read(f)

		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mcin))
		self.mcin.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mtex))
		self.mtex.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mmdx))
		self.mmdx.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mmid))
		self.mmid.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mwmo))
		self.mwmo.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mwid))
		self.mwid.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mddf))
		self.mddf.read(f)
		f.seek(self.mhdr.start_data + int(self.mhdr.ofs_modf))
		self.modf.read(f)
		if int(self.mhdr.ofs_mfbo) and (self.mhdr.flags & ADTHeaderFlags.mhdr_MFBO):
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mfbo))
			self.mfbo.read(f)

		if int(self.mhdr.ofs_mh2o):
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mh2o))
			self.mh2o.read(f)

		if int(self.mhdr.ofs_mtxf):
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mtxf))
			self.mtxf.read(f)

		for row in range(16):
			for col in range(16):
				offset = int(self.mcin.entries[row*16 + col].offset)
				f.seek(offset)
				self.mcnk[row][col].read(f)


	def _prune_unused_layers(self):
		for row in range(16):
			for col in range(16):
				chunk = self.mcnk[row][col]
				for i in range(len(chunk.mcal.layers), 0, -1):
					if chunk.mcal.layers[i-1].is_fully_transparent():
						chunk.remove_texture_layer(i)

	def _prune_unused_textures(self):
		tex_indices = [i for i in range(len(self.mtex.filenames))]
		tex_indices.sort(reverse=True)

		used_tex_indices = {}
		for row in range(16):
			for col in range(16):
				chunk = self.mcnk[row][col]
				for tex_layer in chunk.mcly.layers:
					index = tex_layer.texture_id
					used_tex_indices[index] = True
		
		for k,_ in enumerate(used_tex_indices):
			tex_indices.remove(k)

		for index in tex_indices:
			self.remove_texture_filename(index)

	def _prune_unused_M2s(self):
		m2_indices = [i for i in range(len(self.mmdx.filenames))]
		m2_indices.sort(reverse=True)

		used_m2_indices = {}
		for row in range(16):
			for col in range(16):
				chunk = self.mcnk[row][col]
				
				for doodad_instance in self.mddf.doodad_instances:
					used_m2_indices[doodad_instance.name_id] = True

		for k,_ in enumerate(used_m2_indices):
			m2_indices.remove(k)
		
		for index in m2_indices:
			self.remove_m2_filename(index)

	def _prune_unused_WMOs(self):
		wmo_indices = [i for i in range(len(self.mwmo.filenames))]
		wmo_indices.sort(reverse=True)

		used_wmo_indices = {}
		for row in range(16):
			for col in range(16):
				chunk = self.mcnk[row][col]
				
				for wmo_instance in self.modf.wmo_instances:
					used_wmo_indices[wmo_instance.name_id] = True

		for k,_ in enumerate(used_wmo_indices):
			wmo_indices.remove(k)
		
		for index in wmo_indices:
			self.remove_wmo_filename(index)


	def write(self, write_path=None, optimize=False):
		if not write_path:
			write_path = self.filepath

		if optimize:
			self._prune_unused_layers()
			self._prune_unused_textures()
			self._prune_unused_M2s()
			self._prune_unused_WMOs()
		
		with open(write_path, 'wb') as f:
			self.mver.write(f)
			self.mhdr.write(f)

			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mcin))
			self.mcin.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mtex))
			self.mtex.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mmdx))
			self.mmdx.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mmid))
			self.mmid.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mwmo))
			self.mwmo.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mwid))
			self.mwid.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mddf))
			self.mddf.write(f)
			f.seek(self.mhdr.start_data + int(self.mhdr.ofs_modf))
			self.modf.write(f)

			if int(self.mhdr.ofs_mfbo) and (self.mhdr.flags & ADTHeaderFlags.mhdr_MFBO):
				f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mfbo))
				self.mfbo.write(f)

			if int(self.mhdr.ofs_mh2o):
				f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mh2o))
				self.mh2o.write(f)

			if int(self.mhdr.ofs_mtxf):
				f.seek(self.mhdr.start_data + int(self.mhdr.ofs_mtxf))
				self.mtxf.write(f)

			for row in range(16):
				for col in range(16):
					offset = int(self.mcin.entries[row*16 + col].offset)
					f.seek(offset)
					self.mcnk[row][col].write(f)