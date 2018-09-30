# pywowlib
**pywowlib** is a Python 3.5+ libary featuring the functionality of reading and writing various World of Warcraft related file formats.
The goal of the library is to initially target 3 WoW versions: 3.3.5a, 7.3.5, retail. 
In the future, we may target other core expansion versions: 1.12, 2.4.3, 4.3.4, 5.4.8, 6.2.4

# Supported formats

| Format 	| Description                	| 3.3.5a      	| 7.3.5         	| retail         	| Comment                                                                                                                                                               	|
|--------	|----------------------------	|-------------	|---------------	|---------------	|-----------------------------------------------------------------------------------------------------------------------------------------------------------------------	|
| M2     	| Model                      	| Implemented 	| TBI           	| TBI           	| Legion+ is supported for most structs, but the overall Legion+ workflow is not setup yet                                                                              	|
| Skin   	| M2 LOD file                	| Implemented 	| Implemented ? 	| Implemented ? 	|                                                                                                                                                                       	|
| Anim   	| M2 Animation               	| Implemented 	| TBI           	| TBI           	| Since in Legion+ the file is no longer just raw bytes, that needs to be handled.                                                                                      	|
| Skel   	| M2 Skeleton / Animation    	| -           	| TBI           	| TBI           	|                                                                                                                                                                       	|
| WMO    	| World Map Object           	| Implemented 	| TBI           	| TBI           	| Legion+ is missing a few new chunks, otherwise it is supported.                                                                                                       	|
| ADT    	| Terrain Tile               	| TBI         	| TBI           	| TBI           	| By this category, _tex.adt and other additional ADT-related files are implied as well.                                                                                	|
| WDT    	| World Terrain Layout       	| TBI         	| TBI           	| TBI           	|                                                                                                                                                                       	|
| WDL    	| Lowres Terrain             	| TBI         	| TBI           	| TBI           	|                                                                                                                                                                       	|
| MPQ    	| Storage                    	| Read-only   	| -             	| -             	| Writing can be implemented by extending StormLib Python wrapper that we are using.                                                                                    	|
| CASC   	| Storage (multiple formats) 	| -           	| TBI           	| TBI           	| The plan is to support local reading (making a Python wrapper over Ladislav Zezula's CascLib), as well as some basic CASCHost integration instead of writing support. 	|

# Contribution
Feel free to contribute to the library development by either making a pull request or contacting Skarn directly to gain write access.

# Use
The library comes under MIT license, so feel free to utilize it anywhere you want under MIT license terms.

# Legal note
World of Warcraft is a registered trademark of Blizzard Entertainment and/or other respective owners.
This software is not created by Blizzard Entertainment, and is for purely educational and research purposes.
This software is not intended for the use and production of cheating (hacking) software or modificaitons that can disrupt World of Warcraft's gameplay.
It is your sole responsibility to follow copyright law, game's ToS and EULA. 
The creators hold no responsibility for the consequences of use of this software.
