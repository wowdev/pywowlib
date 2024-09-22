import csv
import os

from bidict import bidict

from enum import IntEnum, Enum
from ..io_utils.types import singleton

__reload_order_index__ = -1


class M2GlobalFlags(IntEnum):
    TILT_X = 0x1
    TILT_Y = 0x2
    UNK_0x4 = 0x4
    UseTextureCombinerCombos = 0x8
    UNK_0x10 = 0x10
    LoadPhysData = 0x20
    UNK_0x40 = 0x40
    UNK_0x80 = 0x80
    CameraRelated = 0x100
    NewParticleRecord = 0x200
    UNK_0x400 = 0x400
    TextureTransformsUseBoneSequences = 0x800
    UNK_0x1000 = 0x1000
    ChunkedAnimFiles = 0x2000
    UNK_0x4000 = 0x4000
    UNK_0x8000 = 0x8000
    UNK_0x10000 = 0x10000
    UNK_0x20000 = 0x20000
    UNK_0x40000 = 0x40000
    UNK_0x80000 = 0x80000
    UNK_0x100000 = 0x100000
    UNK_0x200000 = 0x200000

class M2ParticleFlags(IntEnum):
    LitByLight = 0x1                                       # Particles are affected by lighting;
    Unknown1 = 0x2
    Billboarded = 0x4
    TravelUp = 0x8                                        # Particles travel "up" in world space, rather than model.
    NoTrail = 0x10                                           # Do not Trail
    UnLit = 0x20                                          # Unlightning
    BurstMulti = 0x40
    ModelSpace = 0x80                                       # Particles in Model Space
    Unknown4 = 0x100
    SpawnPosRandom = 0x200                                      # spawn position randomized in some way?
    Pinnned = 0x400                                         # Pinned Particles, their quad enlarges from their creation position to where they expand.
    Unknown5 = 0x800
    XYQuad_Align = 0x1000                                             # XYQuad Particles. They align to XY axis facing Z axis direction.
    GroundClamp = 0x2000                                      # clamp to ground
    Unknown6 = 0x4000
    Unknown7 = 0x8000
    Rng_Texture = 0x10000                               # ChooseRandomTexture
    Outwards = 0x20000                                   # "Outward" particles, most emitters have this and their particles move away from the origin, when they don't the particles start at origin+(speed*life) and move towards the origin.
    Inwards = 0x40000                                           # unknown. In a large proportion of particles this seems to be simply the opposite of the above flag, but in some (e.g. voidgod.m2 or wingedlionmount.m2) both flags are true.
    DisableScaleVary = 0x80000                                       # If set, ScaleVary affects x and y independently; if not set, ScaleVary.x affects x and y uniformly, and ScaleVary.y is not used.
    RngFlip = 0x200000                                # Random FlipBookStart
    IgnoreDistance = 0x400000                                   # Ignores Distance (or 0x4000000?!, CMapObjDef::SetDoodadEmittersIgnoresDistance has this one)
    GravityComp = 0x800000                                  # gravity values are compressed vectors instead of z-axis values (see Compressed Particle Gravity below)
    BoneGen = 0x1000000                                   # bone generator = bone, not joint
    NoThrottle = 0x4000000                           # do not throttle emission rate based on distance
    MultiTexturing = 0x10000000                              # Particle uses multi-texturing (could be one of the other WoD-specific flags), see multi-textured section.


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
    ignore_parent_translate = 0x1,
    ignore_parent_scale = 0x2,
    ignore_parent_rotation = 0x4,
    spherical_billboard = 0x8,
    cylindrical_billboard_lock_x = 0x10,
    cylindrical_billboard_lock_y = 0x20,
    cylindrical_billboard_lock_z = 0x40,
    transformed = 0x200,
    kinematic_bone = 0x400,                                     # MoP+: allow physics to influence this bone
    helmet_anim_scaled = 0x1000,                                # set blend_modificator to helmetAnimScalingRec.m_amount for this bone


class M2SkinMeshPartID(Enum):
    Skin = range(0, 1)
    Hair = range(1, 35)
    Facial1 = range(101, 125)
    Facial2 = range(201, 220)
    Facial3 = range(301, 320)
    Glove = range(401, 406)
    Boots = range(501, 511)
    Shirt = range(601, 615)
    Ears = range(701, 712)
    Wristbands = range(801, 805)
    Kneepads = range(901, 906)
    Chest = range(1001, 1005)
    Pants = range(1101, 1106)
    Tabard = range(1201, 1205)
    Legs = range(1301, 1304)
    ShirtDoublet = range(1401, 1415)
    Cape = range(1501, 1525)
    FacialJewelry = range(1601, 1615)
    EyeEffects = range(1701, 1706)
    Belt = range(1801, 1805)
    Trail = range(1901, 1915)  # Tail?
    Feet = range(2001, 2009)
    # Legion/BFA/SL +
    Head = range(2101, 2102)
    Torso = range(2201, 2203)
    Hands = range(2301, 2302)
    Horns = range (2401, 2425)
    Shoulders = range(2601, 2603)
    Helmet = range(2702, 2703)
    ArmUpper = range(2801, 2850)
    ArmsReplace = range(2901, 2950)
    LegsReplace = range(3001, 3050)
    FeetReplace = range(3101, 3150)
    HeadSwap = range(3201, 3250)
    Eyes = range(3301, 3350)
    Eyebrows = range(3401, 3450)
    Piercings = range(3501, 3550)
    Necklaces = range(3601, 3650)
    Headdress = range(3700, 3750)
    Tail = range(3801, 3850)
    MiscAccessory = range(3901, 3950)
    MiscFeature = range(4001, 4050)
    Noses = range(4101, 4150)
    HairDecoration = range(4201, 4250)
    HornDecoration = range(4301, 4350)
    BodySize = range(4401, 4450)
    Unknown1 = range(4501, 4550)
    Unknown2 = range(4601, 4650)
    Unknown3 = range(4701, 4750)
    Unknown4 = range(4801, 4850)
    Unknown5 = range(4901, 4950)
    Unknown6 = range(5001, 5050)
    EyeGlows = range(5101, 5150)

    @classmethod
    def get_mesh_part_name(cls, mesh_part_id):
        for field in cls:
            if mesh_part_id in field.value:
                return field.name

        print("\nUnknown mesh ID: {}".format(mesh_part_id))
        return 'Unknown'


class M2KeyBones(Enum):

    # official IDs (as of wotlk)

    Arm_L = 0
    Arm_R = 1
    Shoulder_L = 2
    Shoulder_R = 3
    SpineLow = 4
    Waist = 5
    Head = 6
    Jaw = 7
    IndexFinger_R = 8
    MiddleFinger_R = 9
    PinkyFinger_R = 10
    RingFinger_R = 11
    Thumb_R = 12
    IndexFinger_L = 13
    MiddleFinger_L = 14
    PinkyFinger_L = 15
    RingFinger_L = 16
    Thumb_L = 17
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

    # Alastor's guessed IDs

    Ankle_Twist_R = 25
    Ankle_Twist_L = 20
    Ankle_L = 32
    Ankle_R = 35 # FaceAttenuation?
    Cape1 = 36
    Cape2 = 37
    Cape3 = 38
    Cape4 = 39
    Cape5 = 40
    Tail1 = 41
    Tail2 = 42
    TabardBack1 = 43
    TabardBack2 = 44
    TabardBack3 = 45
    Toe_L = 46
    Toe_R = 47
    SpineTop = 48
    Neck1 = 49
    Neck2 = 50
    Pelvis = 51
    Buckle = 52
    Chest = 53
    Main = 54
    Leg_R = 55
    Leg_L = 56
    Knee_R = 57
    Knee_L = 58
    Foot_L = 59
    Foot_R = 60
    Elbow_R = 61
    Elbow_L = 62
    Elbow_Child_L = 63
    Hand_R = 64
    Hand_L = 65
    Weapon_R = 66
    Weapon_L = 67
    Wrist_Child2_L = 68
    Wrist_Child2_R = 69
    Leg_1_Twist3_R = 70
    Leg_1_Twist3_L = 71
    Arm_1_Twist2_R = 72
    Arm_1_Twist2_L = 73
    Arm_1_Twist3_R = 74
    Arm_1_Twist3_L = 75
    Arm_2_Twist2_R = 76
    Arm_2_Twist2_L = 77
    Arm_2_Twist3_R = 78
    Arm_2_Twist3_L = 79
    Forearm_R = 80 
    Forearm_L = 81
    ArmTwist1_R = 82 
    ArmTwist1_L = 83 
    ArmTwist2_R = 84 
    ArmTwist2_L = 85 
    FingerClawA1_R = 86 
    FingerClawB1_R = 87 
    FingerClawA1_L = 88 
    FingerClawB1_L = 89 
    BackCloak = 190 
    face_hair_00_M_JNT = 191 
    face_beard_00_M_JNT = 192 
    face_cheek_02_SkinPoint_L = 193 
    face_cheek_02_SkinPoint_R = 194 
    face_eyeCornerIn_00_SkinPoint_L = 195
    face_eyeCornerIn_00_SkinPoint_R = 196
    face_eyeCornerOut_00_SkinPoint_L = 197
    face_eyeCornerOut_00_SkinPoint_R = 198
    face_eyebrow_00_SkinPoint_L = 199 
    face_eyebrow_00_SkinPoint_M = 200 
    face_eyebrow_00_SkinPoint_R = 201 
    face_eyebrow_01_SkinPoint_L = 202 
    face_eyebrow_01_SkinPoint_R = 203 
    face_eyebrow_02_SkinPoint_L = 204 
    face_eyebrow_02_SkinPoint_R = 205 
    face_eyebrow_03_SkinPoint_L = 206 
    face_eyebrow_03_SkinPoint_R = 207 
    face_eyelidBot_00_SkinPoint_L = 208 
    face_eyelidBot_00_SkinPoint_R = 209 
    face_eyelidBot_01_SkinPoint_L = 210 
    face_eyelidBot_01_SkinPoint_R = 211 
    face_eyelidBot_02_SkinPoint_L = 212 
    face_eyelidBot_02_SkinPoint_R = 213 
    face_eyelidTop_00_SkinPoint_L = 214 
    face_eyelidTop_00_SkinPoint_R = 215 
    face_eyelidTop_01_SkinPoint_L = 216 
    face_eyelidTop_01_SkinPoint_R = 217 
    face_eyelidTop_02_SkinPoint_L = 218 
    face_eyelidTop_02_SkinPoint_R = 219 
    face_noseBridge_00_SkinPoint_L = 220 
    face_noseBridge_00_SkinPoint_R = 221 
    face_overEye_00_SkinPoint_L = 222 
    face_overEye_00_SkinPoint_R = 223 
    face_overOuterEye_00_SkinPoint_L = 224 
    face_overOuterEye_00_SkinPoint_R = 225 
    face_underEye_00_SkinPoint_L = 226 
    face_underEye_00_SkinPoint_R = 227 
    face_cheekPuff_00_SkinPoint_L = 228 
    face_cheekPuff_00_SkinPoint_R = 229 
    face_cheek_00_SkinPoint_L = 230 
    face_cheek_00_SkinPoint_R = 231 
    face_cheek_01_SkinPoint_L = 232 
    face_cheek_01_SkinPoint_R = 233 
    face_chin_00_SkinPoint_L = 234 
    face_chin_00_SkinPoint_M = 235 
    face_chin_00_SkinPoint_R = 236 
    face_ear_00_SkinPoint_L = 237 
    face_ear_00_SkinPoint_R = 238 
    face_jaw_01_SkinPoint_M = 239 
    face_jowl_00_SkinPoint_L = 240 
    face_jowl_00_SkinPoint_R = 241 
    face_jowl_01_SkinPoint_L = 242 
    face_jowl_01_SkinPoint_R = 243 
    face_lipBotBase_00_SkinPoint_M = 244 
    face_lipTopBase_00_SkinPoint_M = 245 
    face_mouthCorner_00_SkinPoint_L = 246 
    face_mouthCorner_00_SkinPoint_R = 247 
    face_mouthCurlBot_00_SkinPoint_M = 248 
    face_mouthCurlTop_00_SkinPoint_M = 249 
    face_mouth_00_SkinPoint_M = 250 
    face_nasLab_00_SkinPoint_L = 251 
    face_nasLab_00_SkinPoint_R = 252 
    face_nasLab_01_SkinPoint_L = 253 
    face_nasLab_01_SkinPoint_R = 254 
    face_noseBase_00_SkinPoint_M = 255 
    face_sneerDriver_00_SkinPoint_L = 256 
    face_sneerDriver_00_SkinPoint_R = 257 
    face_sneerLower_00_SkinPoint_L = 258 
    face_sneerLower_00_SkinPoint_R = 259 
    face_sneer_00_SkinPoint_L = 260 
    face_sneer_00_SkinPoint_R = 261 
    face_teethBot_00_SkinPoint_M = 262 
    face_teethTop_00_SkinPoint_M = 263 
    face_tongue_00_SkinPoint_M = 264 
    root_main_00_SkinPoint_M = 265 
    spine_mainBendy_00_SkinPoint_M = 266 
    clavicle_main_00_SkinPoint_L = 267 
    arm_shoulderBendy_00_SkinPoint_L = 268 
    hand_main_00_JNT_L = 269 
    hand_index_00_SkinPoint_L = 270 
    hand_main_00_SkinPoint_L = 271 
    hand_ring_00_SkinPoint_L = 272 
    hand_pinky_00_SkinPoint_L = 273 
    hand_thumb_00_SkinPoint_L = 274 
    clavicle_main_00_SkinPoint_R = 275 
    arm_shoulderBendy_00_SkinPoint_R = 276 
    hand_main_00_JNT_R = 277 
    hand_main_00_SkinPoint_R = 278 
    hand_middle_00_SkinPoint_R = 279 
    hand_ring_00_SkinPoint_R = 280 
    hand_pinky_00_SkinPoint_R = 281 
    hand_thumb_00_SkinPoint_R = 282 
    head_main_00_SkinPoint_M = 283 
    face_jaw_00_SkinPoint_M = 284 
    Eye1_L = 285 
    Eye1_R = 286 
    EyeLid1_L = 287 
    EyeLid1_R = 288 
    EyeLid2_L = 289 
    EyeLid2_R = 290 
    WingArm1Twist1_L = 292 
    WingArm1Twist1_R = 293
    waterfall_top_sound = 296
    waterfall_bottom_sound = 297

    '''
    guesses based on humanmale_hd

    TabardFront1 = Bone_4
    TabardFront2 = Bone_10
    TabardFront3 = Bone_17

    ToeR = Bone_31
    ToeL = Bone_32
    '''

    @classmethod
    def get_bone_name(cls, keybone_id, bone_crc, idx):
        if keybone_id == -1:  
            crc_name = M2BoneCRCNames.get_bone_name_from_crc(bone_crc)
            if crc_name is None:
                return "Bone_{}".format(idx)
            else:
                return crc_name

        for field in cls:
            if field.value == keybone_id:
                bone_name = field.name
                if bone_name.endswith('_L'):
                    return "{}.{}".format(bone_name[:-2], "L")
                if bone_name.endswith('_R'):
                    return "{}.{}".format(bone_name[:-2], "R")                
                else:
                    return field.name

        print("\nUnknown keybone ID: {}".format(keybone_id))
        return "UNK_Keybone_{}".format(keybone_id)

class M2BoneCRCNames(Enum):
    Toe_R = 3142542542
    Toe_L = 1094736301
    Chest_R = 87406847
    Chest_L = 4282025372
    Neck = 2149808493
    Leg_L = 3947676041
    Leg_R = 289668330
    B_Loin_01 = 1187100303
    F_Loin_01 = 455993219
    Wrist_L = 133952906
    Calf_L = 1475065404
    Calf_R = 2917436255
    Knee_L = 45328125  #4116633036, 2215716567
    Knee_R = 3775641732 #257026223, 2115902388
    B_Loin_02 = 3754485557
    F_Loin_02 = 2183444025
    F_Loin_03 = 4112746159
    CAH = 3987563274
    CPP = 2904086604
    CSS = 524081717
    HIT = 1025530540
    CST = 2170048406
    ESD = 2556568384
    FD1 = 3217595452
    FR0 = 3562477949
    FL0 = 1451682
    BWP = 3818595516
    BWR = 227886480
    SHL = 656719658
    SHR = 3710616137
    TRD = 2627590982
    DTH = 3747058587
    FSD = 2586090777
    SCD = 3389779667
    Ear_01_L = 3985447072
    Eyebrow_R = 2713847615
    Eyebrow_L = 1540176476
    Ear_01_R = 1565210636
    SpineUp = 310207871
    Ear_02_L = 1954826522
    Ear_02_R = 3292686774
    Tail01 = 200542651 #3234909848
    Tail02 = 2466076673
    Object26 = 699064172
    MiddleFinger_Tip_R = 841976507
    IndexFinger_Tip_R = 2353668594
    Thumb_Tip_R = 2319604107
    Thumb_Tip_L = 1884120296
    IndexFinger_Tip_L = 1984240785
    MiddleFinger_Tip_L = 3357587416
    RingFinger_Tip_R = 3157792292
    PinkyFinger_Tip_R = 3380046314
    PinkyFinger_Tip_L = 863523977
    RingFinger_Tip_L = 1178020679
    Plane01 = 2124421159
    Plane02 = 3886631325
    EF_Eyelid01 = 4278575356
    EF_Eyelid_Death = 2435095781
    EyeBow_L = 2602753973
    EyeBow_R = 1630397142
    BWA = 2301297742
    BWS = 2056418566
    Belly = 1236608114
    Plane05 = 2043534398
    Hip_L = 1756834604 #1073108840
    Hip_R = 2461537871 #3321457163
    Spine1_joint = 4256852168
    Spine2_joint = 1991852656
    Eye01 = 1280356454
    Spine3_joint = 3503180228
    Tail1_joint = 1113222609
    LMLeg_joint45 = 4274609575
    RMLeg_joint48 = 3466169200
    LFLeg_joint46 = 374515731
    RFLeg_joint49 = 3356237800
    Tail2_joint = 1941075788
    LMLeg_joint41 = 4188314046
    RMLeg_joint41 = 3074765780
    LFLeg_joint41 = 2285256112
    RFLeg_joint41 = 3336017882
    Tail3_joint = 3586489592
    RLLeg_joint40 = 1541885741
    RLLeg_joint47 = 3313752718
    LMLeg_joint42 = 1622001668
    RMLeg_joint42 = 776757870
    LFLeg_joint42 = 289369098
    RFLeg_joint42 = 1608435296
    Tail4_joint = 274874998
    RLLeg_joint41 = 752910267
    RLLeg_joint42 = 1010067695
    RLLeg_joint42_L = 3051957761
    LMLeg_joint43 = 397080722
    RMLeg_joint43 = 1498108664
    RFLeg_joint43 = 685373174
    RLLeg_joint043 = 1261656185
    RLLeg_joint43 = 3270385303
    RLLeg_joint044 = 3579301338
    HeadScale_joint22 = 2601158378
    LFLeg_joint43 = 1714969756
    FinLeft_joint50 = 1320797406
    FinRight_joint51 = 2639070569
    NoseLeft_joint18 = 3160519086
    Spine1Sale_joint = 1694731022
    Spine2Scale_joint = 4287748709
    Spine3Scale_joint = 1681167882
    TailScale_joint = 244018153
    Tail3Scale_joint = 3056783546
    Taile4Scale_joint = 2568972396
    Hips = 3738240529
    LegBack_01_L = 2118608204
    LegBack_01_R = 1761602358
    SpineUpper = 1688372140
    LegBack_02_L = 3880662262
    LegBack_02_R = 4059478668
    Hump = 2911396259
    LegFront_01_L = 3774419696
    LegFront_01_R = 4131495050
    FootBack_L = 3176988174
    FootBack_R = 1196671853
    LegFront_02_L = 2045789002
    LegFront_02_R = 1867042096
    ToeBack_L = 2211631441
    ToeBack_R = 2044587058
    FootFront_L = 2906586403
    FootFront_R = 1462878272
    ToeFront_L = 1456750441
    ToeFront_R = 2900034058
    Arm1_Twist3_L = 2828305040 #2133193007
    Arm1_Twist3_R = 1385938931 #2234174540
    Elbow_L = 1005774799
    Elbow_R = 3254639276
    Ankle_L = 286571785
    Ankle_R = 3944448106
    Plane04 = 248179880
    SpineLower = 73869075
    Hand_R = 3713458406 #3951430818
    Thumb_L = 2424878462 #3151027085
    Thumb_R = 1787267101 #1105192686
    Lower_01 = 156616400
    Upper_01 = 3862048847
    Lower_02 = 2421987178
    Leg_01_Front_L = 2336852693
    Leg_01_Front_R = 1995865176
    Upper_02 = 2134598133
    Lower_03 = 3881543676
    Leg_01_Middle_L = 2652958531
    Leg_01_Middle_R = 597339540
    Leg_02_Front_L = 96898358
    Leg_02_Front_R = 1333477533
    Upper_03 = 138170723
    Lower_04 = 2034184799
    Leg_01_Back_L = 659936916
    Leg_01_Back_R = 3713723383
    Leg_02_Middle_L = 849488884
    Leg_02_Middle_R = 3366786711
    Leg_03_Front_L = 3379334568
    Leg_03_Front_R = 1476416734
    Upper_04 = 2522399936
    Lower_05 = 238551753
    Leg_02_Back_L = 2849689975
    Leg_02_Back_R = 1406528532
    Leg_03_Middle_L = 3714072778
    Leg_03_Middle_R = 661618089
    Upper_05 = 3781162070
    Lower_06 = 2536592243
    Leg_03_Back_L = 1701892585
    Leg_03_Back_R = 2675960970
    Upper_06 = 2018944492
    Jaw_Top_L = 2734454220
    Jaw_Bottom_L = 2836712998
    Jaw_Top_R = 1492338863
    Jaw_Bottom_R = 1394340677
    Pinky_01_L = 320446612
    Index_01_L = 324882040
    Pinky_01_R = 94449390
    Index_01_R = 98942978
    Pinky_02_L = 2316366126
    Index_02_L = 2320768962
    Pinky_02_R = 2628288340
    Index_02_R = 2632749496
    Pinky_03_L = 4246192568
    Index_03_L = 4250087252
    Pinky_03_R = 3954134978
    Index_03_R = 3958087982
    Foot_L = 117032577 #90603765
    Foot_R = 4244044770 #4285119894
    Finger_L = 1839222075
    Finger_R = 2544857176
    Plane03  = 2427353355
    Arm_L = 2701186468 #4204807211
    Arm_R = 1527769287 #11499848
    Eye_R = 2006816958
    Eye_L = 2375198173
    Hand_L = 660200837 #294203841
    Blid_01_L = 2502312157
    Flid_01_R = 131383389
    Blid_L = 3827894237
    Blid_R = 505821886
    Flid_L = 2142782923
    Flid_R = 2243393704
    GEO_Eyelid_L = 1116453182
    GEO_Eyelid_R = 3095692381
    Cheek_L = 717968576
    Cheek_R = 3502533027
    Geo_EyeLid_Death = 902861035
    fin = 2905535025 

    # online sheet by Marlamin https://docs.google.com/spreadsheets/d/1Ejc6oWYZeNy8I01V3LFtSg6GaGOLdEkTZkTXeo0_Plo/edit#gid=0
    Root = 3066451557
    Main = 521822810
    SpineLow = 40275131
    Chest = 981834931
    Shoulder_R = 3057625618
    Shoulder_L = 1278252913
    C1_Spine2 = 2031597313
    C1_Pelvis1 = 727987715
    Leg_Twist1_L = 4144451481
    Leg_Twist1_R = 3118917107    
    Leg_Twist2_L = 3337573636
    Leg_Twist2_R = 2282684270
    Leg_Twist3_R = 1474856159
    Leg_Twist3_L = 420032181   
    Name = 2738135331
    Head = 130111906
    Breath = 3299126614
    Arm_Twist2_R = 3180860948
    Arm_Twist2_L = 4084841598    
    IndexFinger_R = 995305172
    IndexFinger_L = 3244039095  
    MiddleFinger_R = 80758321
    MiddleFinger_L = 4276058962    
    PinkyFinger_R = 2425597951
    PinkyFinger_L = 1788646044
    RingFinger_L = 2357464676
    RingFinger_R = 1988834055 
    Jaw = 818638717
    Neck2 = 3191706695
    Waist = 3690404639
    Arm_1Twist2_L = 3264325347
    Arm_1Twist2_R = 2356153481    
    Arm_2Twist3_L = 2222886120
    Arm_1Twist3_R = 4218895391
    Arm_1Twist3_L = 3046545013


    @classmethod
    def get_bone_name_from_crc(cls, crc):
        for field in cls:
            if isinstance(field.value, tuple):
                if crc in field.value:
                    bone_name = field.name       
                    if bone_name.endswith('_L'):
                        return "{}.{}".format(bone_name[:-2], "L")
                    if bone_name.endswith('_R'):
                        return "{}.{}".format(bone_name[:-2], "R")                
                    else:
                        return field.name
            else:
                if field.value == crc:
                    bone_name = field.name             
                    if bone_name.endswith('_L'):
                        return "{}.{}".format(bone_name[:-2], "L")
                    if bone_name.endswith('_R'):
                        return "{}.{}".format(bone_name[:-2], "R")                
                    else:
                        return field.name

        return None


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
    VehicleSeat8 = 46
    LeftFoot = 47
    RightFoot = 48
    ShieldNoGlove = 49
    SpineLow = 50
    AlteredShoulderR = 51
    AlteredShoulderL = 52
    BeltBuckle = 53
    SheathCrossbow = 54
    HeadTop = 55
    VirtualSpellDirected = 56
    Backpack = 57
    Unknown = 58
    Unknown2 = 59
    Unknown3 = 60
    Unknown4 = 61
    Unknown5 = 62
    Unknown6 = 63
    Unknown7 = 64
    Unknown8 = 65
    Unknown9 = 66
    Unknown10 = 67
    Unknown11 = 68
    Unknown12 = 69
    Unknown13 = 70
    Unknown14 = 71
    Unknown15 = 72
    Unknown16 = 73
    Unknown17 = 74
    Unknown18 = 75

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
    Unknown7 = '$BWA'
    Unknown8 = '$BWS'

    @classmethod
    def get_event_name(cls, event_token):
        for field in cls:
            if field.value == event_token:
                return field.name

        return None

@singleton
class M2SequenceNames:
    def __init__(self):
        self.animation_names = []
        self.load_animation_data()

    def load_animation_data(self):
        animation_data_path = os.path.join(os.path.dirname(__file__), 'animation_data.csv')
        with open(animation_data_path, newline='') as f:
            csv_reader = csv.reader(f, delimiter=';')
            self.animation_names = [row[1] for row in csv_reader]

    def get_sequence_name(self, seq_id: int):
        if 0 <= seq_id < len(self.animation_names):
            return self.animation_names[seq_id]
        else:
            return None

    def get_sequence_id(self, seq_name: str):
        try:
            return self.animation_names.index(seq_name)
        except ValueError:
            return None

    def items(self):
        return enumerate(self.animation_names)

    def get_anim_ids(self, context):
        return [(str(seq_id), name, '') for seq_id, name in self.items()]