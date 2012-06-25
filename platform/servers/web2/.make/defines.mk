# @auth Travis Fischer
# @acct tfischer
# @date March 2008
# @version 1.0
#
#    This file contains variable and function definitions used by the 
# Makefile subsystem

ifndef __DEFINES_MK__
__DEFINES_MK__ := # Guard against multiple includes

include $(PROJECT_BASE_LIB)/functions.mk

ARCH	:= $(shell uname -m)

endif # __DEFINES_MK__

