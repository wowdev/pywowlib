from collections import OrderedDict
from .types import DBCString, DBCLangString
from ...io_utils.types import *

iRefID = uint32

AnimationData = OrderedDict((
    ('ID', uint32),
    ('Name', DBCString),
    ('WeaponFlags', uint32),
    ('BodyFlags', uint32),
    ('Flags', uint32),
    ('Fallback', uint32),
    ('BehaviorID', uint32),
    ('BehaviorTier', uint32)
))

CharSections = OrderedDict((
    ('ID', uint32),
    ('Race', uint32),
    ('Gender', uint32),
    ('GeneralType', DBCString),
    ('Texture1', DBCString),
    ('Texture2', DBCString),
    ('Texture3', DBCString),
    ('Flags', uint32),
    ('Type', uint32),
    ('Variation', uint32)
))

CreatureDisplayInfo = OrderedDict((
    ('ID', uint32),
    ('Model', uint32),
    ('Sound', uint32),
    ('ExtraDisplayInformation', uint32),
    ('Scale', float32),
    ('Opacity', uint32),
    ('Texture1', DBCString),
    ('Texture2', DBCString),
    ('Texture3', DBCString),
    ('PortraitTextureName', DBCString),
    ('BloodLevel', uint32),
    ('Blood', uint32),
    ('NPCSounds', uint32),
    ('Particles', uint32),
    ('CreatureGeosetData', uint32),
    ('ObjectEffectPackageID', uint32)
))

CreatureDisplayInfoExtra = OrderedDict((
    ('ID', uint32),
    ('Race', iRefID),
    ('Gender', uint32),
    ('SkinColor', uint32),
    ('FaceType', uint32),
    ('HairType', iRefID),
    ('HairStyle', iRefID),
    ('BeardStyle', uint32),
    ('Helm', iRefID),
    ('Shoulder', iRefID),
    ('Shirt', iRefID),
    ('Cuirass', iRefID),
    ('Belt', iRefID),
    ('Legs', iRefID),
    ('Boots', iRefID),
    ('Wrist', iRefID),
    ('Gloves', iRefID),
    ('Tabard', iRefID),
    ('Cape', iRefID),
    ('CanEquip', uint32),
    ('Texture', DBCString)
))

CreatureModelData = OrderedDict((
    ('ID', uint32),
    ('Flags', uint32),
    ('ModelPath', DBCString),
    ('sizeClass', uint32),
    ('modelScale', float32),
    ('BloodLevel', iRefID),
    ('Footprint', iRefID),
    ('footprintTextureLength', float32),
    ('footprintTextureWidth', float32),
    ('footprintParticleScale', float32),
    ('foleyMaterialID', uint32),
    ('footstepShakeSize', iRefID),
    ('deathThudShakeSize', iRefID),
    ('SoundData', iRefID),
    ('CollisionWidth', float32),
    ('CollisionHeight', float32),
    ('mountHeight', float32),
    ('geoBoxMin', vec3D),
    ('geoBoxMax', vec3D),
    ('worldEffectScale', float32),
    ('attachedEffectScale', float32),
    ('missileCollisionRadius', float32),
    ('missileCollisionPush', float32),
    ('missileCollisionRaise', float32)
))

UnitBloodLevels = OrderedDict((
    ('ID', uint32),
    ('ViolenceLevel1', uint32),
    ('ViolenceLevel2', uint32),
    ('ViolenceLevel3', uint32),
))

FootprintTextures = OrderedDict((
    ('ID', uint32),
    ('FootstepFilename', DBCString),
))

CameraShakes = OrderedDict((
    ('ID', uint32),
    ('ShakeType', uint32),
    ('Direction', uint32),
    ('Amplitude', float32),
    ('Frequency', float32),
    ('Duration', float32),
    ('Phase', float32),
    ('Coefficient', float32),
))

ItemDisplayInfo = OrderedDict((
    ('ID', uint32),
    ('LeftModel', DBCString),
    ('RightModel', DBCString),
    ('LeftModelTexture', DBCString),
    ('RightModelTexture', DBCString),
    ('Icon1', DBCString),
    ('Icon2', DBCString),
    ('GeosetGroup1', uint32),
    ('GeosetGroup2', uint32),
    ('GeosetGroup3', uint32),
    ('Flags', uint32),
    ('SpellVisualID', uint32),
    ('GroupSoundIndex', uint32),
    ('HelmetGeosetVis1', uint32),
    ('HelmetGeosetVis2', uint32),
    ('UpperArmTexture', DBCString),
    ('LowerArmTexture', DBCString),
    ('HandsTexture', DBCString),
    ('UpperTorsoTexture', DBCString),
    ('LowerTorsoTexture', DBCString),
    ('UpperLegTexture', DBCString),
    ('LowerLegTexture', DBCString),
    ('FootTexture', DBCString),
    ('ItemVisual', uint32),
    ('ParticleColorID', uint32)
))

ChrRaces = OrderedDict((
    ('ID', uint32),
    ('Flags', uint32),
    ('FactionID', iRefID),
    ('ExplorationSound', iRefID),
    ('MaleModel', iRefID),
    ('FemaleModel', iRefID),
    ('ClientPrefix', DBCString),
    ('BaseLanguage', uint32),
    ('creatureType', iRefID),
    ('ResSicknessSpellID', uint32),
    ('SplashSoundID', uint32),
    ('clientFileString', DBCString),
    ('cinematicSequenceID', iRefID),
    ('alliance', uint32),
    ('RaceNameNeutral', DBCLangString),
    ('RaceNameFemale', DBCLangString),
    ('RaceNameMale', DBCLangString),
    ('facialHairCustomization1', DBCString),
    ('facialHairCustomization2', DBCString),
    ('hairCustomization', DBCString),
    ('required_expansion', uint32)
))

CreatureSoundData = OrderedDict((
    ('ID', uint32),
    ('soundExertionID', iRefID),
    ('soundExertionCriticalID', iRefID),
    ('soundInjuryID', iRefID),
    ('soundInjuryCriticalID', iRefID),
    ('soundInjuryCrushingBlowID', iRefID),
    ('soundDeathID', iRefID),
    ('soundStunID', iRefID),
    ('soundStandID', iRefID),
    ('soundFootstepID', iRefID),
    ('soundAggroID', iRefID),
    ('soundWingFlapID', iRefID),
    ('soundWingGlideID', iRefID),
    ('soundAlertID', iRefID),
    ('soundFidget1', iRefID),
    ('soundFidget2', iRefID),
    ('soundFidget3', iRefID),
    ('soundFidget4', iRefID),
    ('soundFidget', uint32),
    ('customAttack', uint32),
    ('customAttack1', uint32),
    ('customAttack2', uint32),
    ('customAttack3', uint32),
    ('NPCSoundID', iRefID),
    ('loopSoundID', uint32),
    ('creatureImpactType', uint32),
    ('soundJumpStartID', uint32),
    ('soundJumpEndID', uint32),
    ('soundPetAttackID', uint32),
    ('soundPetOrderID', uint32),
    ('soundPetDismissID', iRefID),
    ('fidgetDelaySecondsMin', float32),
    ('fidgetDelaySecondsMax', float32),
    ('birthSoundID', uint32),
    ('spellCastDirectedSoundID', uint32),
    ('submergeSoundID', uint32),
    ('submergedSoundID', uint32),
    ('creatureSoundDataIDPet', uint32),
    ('transformSoundID', uint32),
    ('transformAnimatedSoundID', uint32)
))

CinematicSequences = OrderedDict((
    ('ID', uint32),
    ('soundID', iRefID),
    ('Camera1', iRefID),
    ('Camera2', iRefID),
    ('Camera3', iRefID),
    ('Camera4', iRefID),
    ('Camera5', iRefID),
    ('Camera6', iRefID),
    ('Camera7', iRefID),
    ('Camera8', iRefID)
))

SoundEntries = OrderedDict((
    ('ID', uint32),
    ('SoundType', uint32),
    ('Name', DBCString),
    ('Filename1', DBCString),
    ('Filename2', DBCString),
    ('Filename3', DBCString),
    ('Filename4', DBCString),
    ('Filename5', DBCString),
    ('Filename6', DBCString),
    ('Filename7', DBCString),
    ('Filename8', DBCString),
    ('Filename9', DBCString),
    ('Freq1', DBCString),
    ('Freq2', DBCString),
    ('Freq3', DBCString),
    ('Freq4', DBCString),
    ('Freq5', DBCString),
    ('Freq6', DBCString),
    ('Freq7', DBCString),
    ('Freq8', DBCString),
    ('Freq9', DBCString),
    ('FilePath', DBCString),
    ('Volume', float32),
    ('Flags', uint32),
    ('minDistance', float32),
    ('distanceCutoff', float32),
    ('EAXDef', float32),
    ('soundEntriesAdvancedID', float32)

))

CinematicCamera = OrderedDict((
    ('ID', uint32),
    ('Filepath', DBCString),
    ('Voiceover', iRefID),
    ('X', float32),
    ('Y', float32),
    ('Z', float32),
    ('Rotation', float32)
))

HelmetGeosetVisData = OrderedDict((
    ('ID', uint32),
    ('HairFlags', uint32),
    ('Facial1Flags', uint32),
    ('Facial2Flags', uint32),
    ('Facial3Flags', uint32),
    ('EarsFlags', uint32),
    ('Unknown1', uint32),
    ('Unknown2', uint32)
))

ItemVisuals = OrderedDict((
    ('ID', uint32),
    ('VisualEffect1', iRefID),
    ('VisualEffect2', iRefID),
    ('VisualEffect3', iRefID),
    ('VisualEffect4', iRefID),
    ('VisualEffect5', iRefID)
))

ItemVisualEffects = OrderedDict((
    ('ID', uint32),
    ('Effect', DBCString)
))

ItemGroupSounds = OrderedDict((
    ('ID', uint32),
    ('Pickup', iRefID),
    ('PutDown', iRefID),
    ('Unknown1', iRefID),
    ('Unknown2', iRefID)
))

