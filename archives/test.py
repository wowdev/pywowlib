from mpq import MPQFile

mpq = MPQFile("/Users/sshumakov/Documents/WoW Modding/World of Warcraft 3.3.5a/Data/patch-3.mpq", 0x00000100)
print(mpq.printdir())