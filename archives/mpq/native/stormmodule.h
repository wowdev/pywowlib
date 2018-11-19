#ifndef Py_STORMMODULE_H
#define Py_STORMMODULE_H
#include <StormLib.h>

#ifdef __cplusplus
extern "C" {
#endif

#ifdef STORM_MODULE
/* This section is used when compiling stormmodule.c */

#else
/* This section is used in modules that use stormmodule's API */

static void **PyStorm_API;

#endif

#ifdef __cplusplus
}
#endif

#endif /* !defined(Py_STORMMODULE_H) */
