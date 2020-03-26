from enum import IntEnum
from .. import WoWVersionManager, WoWVersions

__reload_order_index__ = -1


class ADTChunkFlags(IntEnum):
	HAS_MCSH				= 0b1 << 0
	IMPASS					= 0b1 << 1
	LQ_RIVER				= 0b1 << 2
	LQ_OCEAN				= 0b1 << 3
	LQ_MAGMA				= 0b1 << 4
	LQ_SLIME				= 0b1 << 5
	HAS_MCCV				= 0b1 << 6
	UNKNOWN					= 0b1 << 7
	# +7 bits
	DO_NOT_FIX_ALPHA_MAP	= 0b1 << 15
	HIGH_RES_HOLES			= 0b1 << 16
	# +15 bits

class ADTAlphaSize(IntEnum):
	LOWRES		= 2048
	HIGHRES		= 4096


class ADTAlphaTypes(IntEnum):
	#    MCLY flags    |    WDT MPHD flags    |    MCNK flags    |    mode
	#------------------------------------------------------------------------------------
	#                  |                      |                  |    "BROKEN" (2048)
	#                  |                      |    0x8000 set    |    Uncompressed (2048)
	#                  |    0x4 or 0x80 set   |    0x8000 set    |    Uncompressed (4096)
	#     0x200 set    |    0x4 or 0x80 set   |    0x8000 set    |    Compressed (4096)
	BROKEN				= 0
	LOWRES				= 1
	HIGHRES				= 2
	HIGHRES_COMPRESSED	= 3


class ADTHeaderFlags(IntEnum):
	mhdr_MFBO		= 0b1 << 0			# contains a MFBO chunk.
	mhdr_northrend	= 0b1 << 1			# is set for some northrend ones.


class ADTDoodadDefinitionFlags(IntEnum):
	mddf_biodome				= 0b1 << 0		# this sets eevee flags to | 0x800 (WDOODADDEF.var0xC).
	mddf_shrubbery				= 0b1 << 1		# the actual meaning of these is unknown to me. maybe biodome is for really big M2s. 6.0.1.18179 seems
												# not to check  for this flag
	mddf_unk_4					= 0b1 << 2		# Legion+ᵘ
	mddf_unk_8					= 0b1 << 3		# Legion+ᵘ
	#							= 0b1 << 4
	mddf_liquidKnown			= 0b1 << 5		# Legion+ᵘ
	mddf_entry_is_filedata_id	= 0b1 << 6		# Legion+ᵘ nameId is a file data id to directly load
	#							= 0b1 << 7
	mddf_unk_100				= 0b1 << 8		# Legion+ᵘ


class ADTObjectDefinitionFlags(IntEnum):
	modf_destroyable			= 0b1 << 0		# set for destroyable buildings like the tower in DeathknightStart. This makes it a server-controllable game object.
	modf_use_lod				= 0b1 << 1		# WoD(?)+: also load _LOD1.WMO for use dependent on distance
	modf_unk_has_scale			= 0b1 << 2		# Legion+: if this flag is set then use scale = scale / 1024, otherwise scale is 1.0
	modf_entry_is_filedata_id	= 0b1 << 3		# Legion+: nameId is a file data id to directly load //SMMapObjDef::FLAG_FILEDATAID


class ADTChunkLayerFlags(IntEnum):
	animation_rotation0		= 0b1 << 0		# each tick is 45°
	animation_rotation1		= 0b1 << 1
	animation_rotation2		= 0b1 << 2
	animation_speed0		= 0b1 << 3
	animation_speed1		= 0b1 << 4
	animation_speed2		= 0b1 << 5
	animation_enabled		= 0b1 << 6
	overbright				= 0b1 << 7		# This will make the texture way brighter. Used for lava to make it "glow".
	use_alpha_map			= 0b1 << 8		# set for every layer after the first
	alpha_map_compressed	= 0b1 << 9		# see MCAL chunk description
	use_cube_map_reflection	= 0b1 << 10		# This makes the layer behave like its a reflection of the skybox. See below
	unknown_0x800			= 0b1 << 11		# WoD?+ if either of 0x800 or 0x1000 is set, texture effects' texture_scale is applied
	unknown_0x1000			= 0b1 << 12		# WoD?+ see 0x800
	# +19 bits


class ADTTextureFlags(IntEnum):
	do_not_load_specular_or_height_texture_but_use_cubemap	= 0b1 << 0	# probably just 'disable_all_shading'
	unused0				= 0b1 << 1		# no non-zero values in 20490
	unused1				= 0b1 << 2		# no non-zero values in 20490
	unused2				= 0b1 << 3		# no non-zero values in 20490
	if WoWVersionManager().client_version >= WoWVersions.MOP:
		texture_scale0	= 0b1 << 4
		texture_scale1	= 0b1 << 5
		texture_scale2	= 0b1 << 6
		texture_scale3	= 0b1 << 7
		# +24 bits						# no non-zero values in 20490
	# else
		# +28 unused bits				# no non-zero values in 20490


class ADTLodLiquidDataFlags(IntEnum):
	Flag_HasTileData	= 0b1 << 0
	_compressed_A		= 0b1 << 1
	_compressed_B		= 0b1 << 2