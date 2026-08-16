CC = gcc
OPT = -O0 -Wall -g

OSTYPE := $(shell uname)

#
# LINUX SECTION
#
ifneq (,$(findstring Linux,$(OSTYPE)))
ARCH_OPT = -DHAVE_MMAP
PIC = -fpic
DL = -ldl
#SO_CMD = -shared -Wl,--export-dynamic
LIB_CMD = -shared
# Flags given to the linker to indicate places to look for libraries
LIB_FLAGS = -Wl,-rpath,./ -Wl,-rpath,$(CURDIR) -Wl,-rpath,$(CURDIR)/libs -Wl,-rpath,$(CURDIR)/libs/libpoker-eval
LIB_EXT = .so
EXE_EXT =
PVAT_LIB = lib-pvat$(LIB_EXT)
endif

#
# MAC OSX SECTION
#
ifneq (,$(findstring Darwin,$(OSTYPE)))
ARCH_OPT = -DHAVE_MMAP -arch x86_64
DL = -ldl
PIC = -fPIC
#SO_CMD = -bundle -undefined dynamic_lookup
LIB_CMD = -dynamiclib -undefined dynamic_lookup
LIB_FLAGS =
LIB_EXT = .dylib
EXE_EXT =
# -fno-common needed when compiling libraries
OPT += -fno-common
PVAT_LIB = lib-pvat$(LIB_EXT)
endif

#
# CYGWIN SECTION
#
ifneq (,$(findstring cygwin,$(OSTYPE))$(findstring CYGWIN,$(OSTYPE)))
ARCH_OPT = -DHAVE_MMAP
PIC =
DL =
#SO_CMD = -shared -Wl,--export-dynamic
LIB_CMD = -shared
# Flags given to the linker to indicate places to look for libraries
LIB_FLAGS = -Wl,-rpath,$(CURDIR) -Wl,-rpath,$(CURDIR)/libs
LIB_EXT = .dll
EXE_EXT = .exe
PVAT_LIB = cyg-pvat$(LIB_EXT)
endif


#----------------------------------------------------------------------
# CFLAGS AND LIBS
#----------------------------------------------------------------------
CFLAGS = $(ARCH_OPT) $(OPT) -I./libs -I./libs/include/poker-eval
LIBS = -L./libs -l-pvat -L./libs/libpoker-eval -lpoker-eval -lm $(LIB_FLAGS)
# Export the flags so that the libs use the same variables
export CC CFLAGS PIC LIB_CMD ARCH_OPT

PVAT = $(addsuffix $(EXE_EXT), open_pvat)

all: $(PVAT)

library: libs/$(PVAT_LIB)

clean: 
	rm -f *.o $(PVAT)
	cd libs; make clean;

# The dynamic library
libs/$(PVAT_LIB): libs/*.c libs/*.h
	cd libs && $(MAKE) $(PVAT_LIB)
ifneq (,$(findstring cygwin,$(OSTYPE))$(findstring CYGWIN,$(OSTYPE)))
	cp libs/$(PVAT_LIB) .
endif

#pvat target
open_pvat$(EXE_EXT): open_pvat.c open_pvat.h open_pvat_reader.c open_pvat_reader.h libs/$(PVAT_LIB)
	$(CC) $(CFLAGS) -DPVAT_MAIN open_pvat.c open_pvat_reader.c $(LIBS) $(DL) -o $@
	chmod 755 $@