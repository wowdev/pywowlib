from enum import IntEnum, Enum

__reload_order_index__ = -1


class M2GlobalFlags(IntEnum):
    TILT_X = 0x1
    TILT_Y = 0x2
    UseTextureCombinerCombos = 0x8
    LoadPhysData = 0x20
    UNK = 0x80
    CameraRelated = 0x100


class M2ParticleFlags(IntEnum):
    EffectedByLight = 0x1                                       # Particles are affected by lighting;
    Unknown1 = 0x2
    Unknown2 = 0x4
    UseWorldMatrix = 0x8                                        # Particles travel "up" in world space, rather than model.
    DoNotTrail = 0x10                                           # Do not Trail
    Unlightning = 0x20                                          # Unlightning
    Unknown3 = 0x40
    UseModelMatrix = 0x80                                       # Particles in Model Space
    Unknown4 = 0x100
    SpawnPosRandom = 0x200                                      # spawn position randomized in some way?
    PinParticle = 0x400                                         # Pinned Particles, their quad enlarges from their creation position to where they expand.
    Unknown5 = 0x800
    XYQuad = 0x1000                                             # XYQuad Particles. They align to XY axis facing Z axis direction.
    ClampToGround = 0x2000                                      # clamp to ground
    Unknown6 = 0x4000
    Unknown7 = 0x8000
    ChooseRandomTexture = 0x10000                               # ChooseRandomTexture
    OutwardParticle = 0x20000                                   # "Outward" particles, most emitters have this and their particles move away from the origin, when they don't the particles start at origin+(speed*life) and move towards the origin.
    Unknown = 0x40000                                           # unknown. In a large proportion of particles this seems to be simply the opposite of the above flag, but in some (e.g. voidgod.m2 or wingedlionmount.m2) both flags are true.
    ScaleVaryXY = 0x80000                                       # If set, ScaleVary affects x and y independently; if not set, ScaleVary.x affects x and y uniformly, and ScaleVary.y is not used.
    RandFlipBookStart = 0x200000                                # Random FlipBookStart
    IgnoreDistance = 0x400000                                   # Ignores Distance (or 0x4000000?!, CMapObjDef::SetDoodadEmittersIgnoresDistance has this one)
    CompressGravity = 0x800000                                  # gravity values are compressed vectors instead of z-axis values (see Compressed Particle Gravity below)
    BoneGenerator = 0x1000000                                   # bone generator = bone, not joint
    DoNotThrottleEmission = 0x4000000                           # do not throttle emission rate based on distance
    UseMultiTexturing = 0x10000000                              # Particle uses multi-texturing (could be one of the other WoD-specific flags), see multi-textured section.


class M2TextureTypes(IntEnum):
    NONE = 0                                                    # Texture given in filename
    SKIN = 1                                                    # Skin Body + clothes
    OBJECT_SKIN = 2                                             # Object Skin -- Item, Capes ("Item\ObjectComponents\Cape\*.blp")
    WEAPON_BLADE = 3                                            # Weapon Blade -- Used on several models but not used in the client as far as I see. Armor Reflect?
    WEAPON_HANDLE = 4                                           # Weapon Handle
    ENVIRONMENT = 5                                             # (OBSOLETE) Environment (Please remove from source art)
    CHAR_HAIR = 6                                               # Skin Body + clothes
    CHAR_FACIAL_HAIR = 7                                        # (OBSOLETE) Character Facial Hair (Please remove from source art)
    SKIN_EXTRA = 8                                              # Skin Extra
    UI_SKIN = 9                                                 # UI Skin -- Used on inventory art M2s (1): inventoryartgeometry.m2 and inventoryartgeometryold.m2
    TAUREN_MANE = 10                                            # (OBSOLETE) Tauren Mane (Please remove from source art) -- Only used in quillboarpinata.m2. I can't even find something referencing that file. Oo Is it used?
    MONSTER_1 = 11                                              # Monster Skin 1 -- Skin for creatures or gameobjects #1
    MONSTER_2 = 12                                              # Monster Skin 2 -- Skin for creatures or gameobjects #2
    MONSTER_3 = 13                                              # Monster Skin 3 -- Skin for creatures or gameobjects #3
    ITEM_ICON = 14                                              # Item Icon -- Used on inventory art M2s (2): ui-button.m2 and forcedbackpackitem.m2 (CSimpleModel_ReplaceIconTexture("texture"))

    # Cata+
    GUILD_BG_COLOR = 15
    GUILD_EMBLEM_COLOR = 16
    GUILD_BORDER_COLOR = 17
    GUILD_EMBLEM = 18


class M2LightTypes(IntEnum):
    Directional = 0                                             # Directional light type is not used (at least in 3.3.5) outside login screen, and doesn't seem to be taken into account in world.
    Point = 1


class M2TextureFlags(IntEnum):
    T_WRAP_X = 0x1
    T_WRAP_Y = 0x2


class M2RenderFlags(IntEnum):
    Unlit = 0x1
    Unfogged = 0x2
    TwoSided = 0x8
    DepthWrite = 0x10
    ShadowBatch1 = 0x40
    ShadowBatch2 = 0x80
    UnkWoD = 0x400
    PreventAlpha = 0x800


class M2BlendingModes(IntEnum):
    Opaque = 0
    Mod = 1
    Decal = 2
    Add = 3
    Mod2X = 4
    Fade = 5
    DeeprunTram = 6
    WoD = 7


class M2CompBoneFlags(IntEnum):
    spherical_billboard = 0x8,
    cylindrical_billboard_lock_x = 0x10,
    cylindrical_billboard_lock_y = 0x20,
    cylindrical_billboard_lock_z = 0x40,
    transformed = 0x200,
    kinematic_bone = 0x400,                                     # MoP+: allow physics to influence this bone
    helmet_anim_scaled = 0x1000,                                # set blend_modificator to helmetAnimScalingRec.m_amount for this bone


class M2SkinMeshPartID(Enum):
    Skin = range(0, 1)
    Hair = range(1, 22)
    Facial1 = range(101, 109)
    Facial2 = range(201, 207)
    Facial3 = range(301, 312)
    Glove = range(401, 405)
    Boots = range(501, 506)
    Unknown = range(601, 615)
    Ears = range(701, 703)
    Wristbands = range(801, 804)
    Kneepads = range(901, 904)
    Chest = range(1001, 1005)
    Pants = range(1101, 1105)
    Tabard = range(1201, 1203)
    Legs = range(1301, 1303)
    Unknown2 = range(1401, 1415)
    Cloak = range(1501, 1511)
    Unknown3 = range(1601, 1615)
    Eyeglows = range(1701, 1704)
    Belt = range(1801, 1803)
    Tail = range(1901, 1915)
    Feet = range(2001, 2003)
    # Legion +
    Hands = range(2301, 2302)

    @classmethod
    def get_mesh_part_name(cls, mesh_part_id):
        for field in cls:
            if mesh_part_id in field.value:
                return field.name

        print("\nUnknown mesh ID: {}".format(mesh_part_id))
        return None


class M2KeyBones(Enum):
    ArmL = 0
    ArmR = 1
    ShoulderL = 2
    ShoulderR = 3
    SpineLow = 4
    Waist = 5
    Head = 6
    Jaw = 7
    IndexFingerR = 8
    MiddleFingerR = 9
    PinkyFingerR = 10
    RingFingerR = 11
    ThumbR = 12
    IndexFingerL = 13
    MiddleFingerL = 14
    PinkyFingerL = 15
    RingFingerL = 16
    ThumbL = 17
    BTH = 18
    CSR = 19
    CSL = 20
    _Breath = 21
    _Name = 22
    _NameMount = 23
    CHD = 24
    CCH = 25
    Root = 26
    Wheel1 = 27
    Wheel2 = 28
    Wheel3 = 29
    Wheel4 = 30
    Wheel5 = 31
    Wheel6 = 32
    Wheel7 = 33
    Wheel8 = 34

    @classmethod
    def get_bone_name(cls, keybone_id, idx):
        if keybone_id == -1:
            return "Bone_{}".format(idx)

        for field in cls:
            if field.value == keybone_id:
                return field.name

        print("\nUnknown keybone ID: {}".format(keybone_id))
        return "UNK_Keybone"


class M2AttachmentTypes(Enum):
    Shield_MountMain_ItemVisual0 = 0
    HandRight_ItemVisual1 = 1
    HandLeft_ItemVisual2 = 2
    ElbowRight_ItemVisual3 = 3
    ElbowLeft_ItemVisual4 = 4
    ShoulderRight = 5
    ShoulderLeft = 6
    KneeRight = 7
    KneeLeft = 8
    HipRight = 9
    HipLeft = 10
    Helm = 11
    Back = 12
    ShoulderFlapRight = 13
    ShoulderFlapLeft = 14
    ChestBloodFront = 15
    ChestBloodBack = 16
    Breath = 17
    PlayerName = 18
    Base = 19
    Head = 20
    SpellLeftHand = 21
    SpellRightHand = 22
    Special1 = 23
    Special2 = 24
    Special3 = 25
    SheathMainHand = 26
    SheathOffHand = 27
    SheathShield = 28
    PlayerNameMounted = 29
    LargeWeaponLeft = 30
    LargeWeaponRight = 31
    HipWeaponLeft = 32
    HipWeaponRight = 33
    Chest = 34
    HandArrow = 35
    Bullet = 36
    SpellHandOmni = 37
    SpellHandDirected = 38
    VehicleSeat1 = 39
    VehicleSeat2 = 40
    VehicleSeat3 = 41
    VehicleSeat4 = 42
    VehicleSeat5 = 43
    VehicleSeat6 = 44
    VehicleSeat7 = 45
    VehicleSeat8 = 47
    LeftFoot = 48
    RightFoot = 49
    ShieldNoGlove = 50
    SpineLow = 51
    AlteredShoulderR = 52
    AlteredShoulderL = 53
    BeltBuckle = 54
    SheathCrossbow = 55
    HeadTop = 56

    @classmethod
    def get_attachment_name(cls, attachment_id, idx):
        for field in cls:
            if field.value == attachment_id:
                return "Att_{}".format(field.name)

        return "Att_{}".format(str(idx).zfill(3))


class M2EventTokens(Enum):
    """This is most likely partially or entirely wrong. Names are mostly based on function names and pure guesswork."""

    # soundEffect ID is defined by CreatureSoundDataRec::m_customAttack[x]
    CustomAttack1 = '$AH0'
    PlaySoundKitCustomAttack2 = '$AH1'
    PlaySoundKitCustomAttack3 = '$AH2'
    PlaySoundKitCustomAttack4 = '$AH3'

    BowMissleDestination = "$BMD"
    MissileFirePos = '$AIM'
    DisplayTransition = '$ALT'

    FootstepLeftBackwards1 = '$BL0'
    FootstepLeftBackwards2 = '$BL1'
    FootstepLeftBackwards3 = '$BL2'
    FootstepLeftBackwards4 = '$BL3'
    FootstepRightBackwards1 = '$BR0'
    FootstepRightBackwards2 = '$BR1'
    FootstepRightBackwards3 = '$BR2'
    FootstepRightBackwards4 = '$BR3'

    FootstepLeftForward1 = '$FL0'
    FootstepLeftForward2 = '$FL1'
    FootstepLeftForward3 = '$FL2'
    FootstepLeftForward4 = '$FL3'
    FootstepRightForward1 = '$FR0'
    FootstepRightForward2 = '$FR1'
    FootstepRightForward3 = '$FR2'
    FootstepRightForward4 = '$FR3'

    FootstepLeftRunning1 = '$RL0'
    FootstepLeftRunning2 = '$RL1'
    FootstepLeftRunning3 = '$RL2'
    FootstepLeftRunning4 = '$RL3'
    FootstepRightRunning1 = '$RR0'
    FootstepRightRunning2 = '$RR1'
    FootstepRightRunning3 = '$RR2'
    FootstepRightRunning4 = '$RR3'

    FootstepLeftStop1 = '$SL0'
    FootstepLeftStop2 = '$SL1'
    FootstepLeftStop3 = '$SL2'
    FootstepLeftStop4 = '$SL3'
    FootstepRightStop1 = '$SR0'
    FootstepRightStop2 = '$SR1'
    FootstepRightStop3 = '$SR2'
    FootstepRightStop4 = '$SR3'

    FootstepLeftWalk1 = '$WL0'
    FootstepLeftWalk2 = '$WL1'
    FootstepLeftWalk3 = '$WL2'
    FootstepLeftWalk4 = '$WL3'

    FootstepRightWalk1 = '$WR0'
    FootstepRightWalk2 = '$WR1'
    FootstepRightWalk3 = '$WR2'
    FootstepRightWalk4 = '$WR3'

    PlaySoundKitBirth = '$BRT'                                  # soundEffect ID is defined by CreatureSoundDatarec::m_birthSoundID
    Breath = '$BTH'                                             # All situations, where nothing happens or breathing.
    PlayRangedItemPull = '$BWP'                                 # LoadRifle, LoadBow
    BowRelease = '$BWR'                                         # AttackRifle, AttackBow, AttackThrown
    AttackHold = '$CAH'                                          # Attack*, *Unarmed, ShieldBash, Special*
    AttackThrown = '$CCH'                                       # CEffect::DrawFishingString needs this on the model for getting the string attachments.
    UpdateMountHeightOrOffset = '$CFM'                          # CGCamera::UpdateMountHeightOrOffset: Only z is used. Non-animated. Not used if $CMA
    Unknown1 = '$CHD'                                           # Does not exist?
    CameraPosition = '$CMA'
    PlayCombatActionAnimKit = '$CPP'                            # parry, anims, depending on some state, also some callback which might do more
    PlayEmoteSound = '$CSD'                                     # data: soundEntryId
    ReleaseMissilesLeft = '$CSL'                                # AttackRifle, SpellCast*, ChannelCast
    ReleaseMissilesRight = '$CSR'                               # AttackBow, AttackRifle, AttackThrown, SpellCast*, ChannelCast*
    PlayWeaponSwooshSound = '$CSS'
    ReleaseMissiles = '$CST'                                    # SpellCast, Parry*, EmoteEat, EmoteRoar, Kick, ...
    PlaySoundEntryAdvanced = '$CVS'                             # Data: SoundEntriesAdvanced.dbc, Sound — Not present in 6.0.1.18179
    DestroyEmitter = '$DSE'
    DoodadSoundUnknown = '$DSL'                                 # Gameobjects,  data: soundEntryId
    DoodadSoundOneShot = '$DSO'                                 # data: soundEntryId
    Death = '$DTH'                                              # DeathThud + LootEffect,
    ObjectPackageEnterState2 = '$EWT'
    ObjectPackageEnterState3 = '$EAC'
    ObjectPackageEnterState4 = '$EMV'
    ObjectPackageEnterState5 = '$EDC'

    PlayEmoteStateSound = '$ESD'

    # CreatureSoundDataRec::m_soundFidget (only has 5 entries, so don’t use 6-9) # TODO: scan client if 6-9 are used
    PlayFidgetSound1 = '$FD1'
    PlayFidgetSound2 = '$FD2'
    PlayFidgetSound3 = '$FD3'
    PlayFidgetSound4 = '$FD4'
    PlayFidgetSound5 = '$FD5'

    PlayUnitSound = '$FDX'                                      # soundEffect ID is defined by CreatureSoundDataRec::m_soundStandID. Stand.
    HandleFootfallAnimEvent = '$FSD'                            # Plays some sound. Footstep? Also seen at several emotes etc. where feet are moved. CGUnit_C::HandleFootfallAnimEvent

    GOPlayAnimatedSoundCustom1 = '$GC0'
    GOPlayAnimatedSoundCustom2 = '$GC1'
    GOPlayAnimatedSoundCustom3 = '$GC2'
    GOPlayAnimatedSoundCustom4 = '$GC3'
    GOPlayAnimatedSound1 = '$GO0'
    GOPlayAnimatedSound2 = '$GO1'
    GOPlayAnimatedSound3 = '$GO2'
    GOPlayAnimatedSound4 = '$GO3'
    PlayWoundAnimKit = '$HIT'                                   # Attack*, *Unarmed, ShieldBash, Special*, soundEntryId depends on SpellVisualKit
    MapLoadUnknown = '$KVS'                                     # MapLoad.cpp -- not found in 6.0.1.18179

    SpellCastDirectedSound = '$SCD'                             # soundEffect ID is defined by CreatureSoundDataRec::m_spellCastDirectedSoundID
    GOAddShake = '$SHK'                                         # data: spellEffectCameraShakesID
    ExchangeSheathedWeaponLeft = '$SHL'                         # Sheath, HipSheath
    ExchangeSheathedWeaponRight = '$SHR'                        # Sheath, HipSheath

    PlaySoundKitSubmerged = '$SMD'                              # soundEffect ID is defined by CreatureSoundDatarec::m_submergedSoundID
    PlaySoundKitSubmerge = '$SMG'                               # soundEffect ID is defined by CreatureSoundDatarec::m_submergeSoundID
    GOPlaySoundKitCustom = '$SND'
    MountTransitionObjectE = '$STE'                             # Not seen in 6.0.1.18179 -- x is {E and B} , sequence time is taken of both, pivot of $STB. (Also, attachment info for attachment 0)
    MountTransitionObjectB = '$STB'
    HandleSpellEventSound = '$TRD'                              # EmoteWork*, UseStanding*, soundEffect ID is implicit by SpellRec

    HandleBoneAnimGrabEvent1 = '$VG0'
    HandleBoneAnimGrabEvent2 = '$VG1'
    HandleBoneAnimGrabEvent3 = '$VG2'
    HandleBoneAnimGrabEvent4 = '$VG3'
    HandleBoneAnimGrabEvent5 = '$VG4'
    HandleBoneAnimGrabEvent6 = '$VG5'
    HandleBoneAnimGrabEvent7 = '$VG6'
    HandleBoneAnimGrabEvent8 = '$VG7'
    HandleBoneAnimGrabEvent9 = '$VG8'

    HandleBoneAnimThrowEvent1 = '$VT0'
    HandleBoneAnimThrowEvent2 = '$VT1'
    HandleBoneAnimThrowEvent3 = '$VT2'
    HandleBoneAnimThrowEvent4 = '$VT3'
    HandleBoneAnimThrowEvent5 = '$VT4'
    HandleBoneAnimThrowEvent6 = '$VT5'
    HandleBoneAnimThrowEvent7 = '$VT6'
    HandleBoneAnimThrowEvent8 = '$VT7'
    HandleBoneAnimThrowEvent9 = '$VT8'

    PlayUnitSoundWingGlide = '$WGG'
    PlayUnitSoundWingFlap = '$WNG'
    WeaponTrailBottomPos = '$WTB'
    WeaponTrailTopPos = '$WTT'
    Unknown2 = '$WWG'                                           # Calls some function in the Object VMT. -- Not seen in 6.0.1.18179
    ExploadBallista = 'DEST'
    Unknown3 = 'POIN'
    Unknown4 = 'WHEE'                                           # Data: 601+, Used on wheels at vehicles.
    Unknown5 = 'BOTT'                                           # seen in well_vortex01.m2
    Unknown6 = 'TOP'                                            # seen in well_vortex01.m2

    @classmethod
    def get_event_name(cls, event_token):
        for field in cls:
            if field.value == event_token:
                return field.name

        return None












