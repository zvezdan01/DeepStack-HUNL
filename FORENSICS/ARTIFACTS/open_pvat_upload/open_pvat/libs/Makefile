LIBS = poker-eval
LIBS_A = $(addsuffix .a, $(LIBS))
MODULES = hand_strength game_state open_pvat_utils open_pvat_table pvat_defines
MODULES_O = $(addsuffix .o,$(MODULES))

OSTYPE := $(shell uname)

ifneq (,$(findstring Darwin,$(OSTYPE)))
CONFIGUREFLAGS = CC="gcc -arch x86_64" LDFLAGS="-Wl,-arch,x86_64"
endif

CFLAGS += -I include/poker-eval $(PIC)

clean:
	rm -f *.o *.il lib-pvat* cyg.dll;
	rm -f .finished_poker-eval
	cd poker-eval-136.0; make clean;

.finished_poker-eval:
	cd poker-eval-136.0; $(CONFIGUREFLAGS) ./configure --prefix $(PWD) --libdir $(PWD)/libpoker-eval/; make install; cd ..; #mv lib libpoker-eval;
#cp -f configure.org configure; cp -f include/poker_config.h.org include/poker_config.h
	touch .finished_poker-eval

open_pvat_utils.h: game_state.h
	touch $@

open_pvat_utils.o: open_pvat_utils.c open_pvat_utils.h hand_strength.h
	$(CC) $(CFLAGS) -c $< -o $@

open_pvat_table.o: open_pvat_table.c open_pvat_table.h
	$(CC) $(CFLAGS) -c $< -o $@

game_state.o: game_state.c game_state.h
	$(CC) $(CFLAGS) -c $< -o $@

hand_strength.o: hand_strength.c hand_strength.h
	$(CC) $(CFLAGS) -c $< -o $@

pvat_defines.o: pvat_defines.c pvat_defines.h
	$(CC) $(CFLAGS) -c $< -o $@

# UNIX / Linux dynamic library
lib-pvat.so: lib-pvat.so.1
	ln -sf lib-pvat.so.1 lib-pvat.so

lib-pvat.so.1: lib-pvat.so.1.0
	ln -sf lib-pvat.so.1.0 lib-pvat.so.1

lib-pvat.so.1.0: .finished_poker-eval $(MODULES_O)
	$(CC) $(LIB_CMD) -Wl,-soname,lib-pvat.so.1 $(MODULES_O) -o $@

# Mac dynamic library
lib-pvat.dylib: lib-pvat.1.dylib
	ln -sf lib-pvat.1.dylib lib-pvat.dylib

lib-pvat.1.dylib: lib-pvat.1.0.dylib
	ln -sf lib-pvat.1.0.dylib lib-pvat.1.dylib

lib-pvat.1.0.dylib: $(MODULES_O) tree_stub.o
# Note that install_name should pass the complete path to the library,
# and not just a relative path like ./poker-utils/ .
	$(CC) $(ARCH_OPT) $(LIB_CMD) -install_name $(CURDIR)/lib-pvat.1.0.dylib $(MODULES_O) tree_stub.o -o $@

# Windows dynamic link library
cyg-pvat.dll: $(MODULES_O) tree_stub.o
	$(CC) $(ARCH_OPT) $(LIB_CMD) $(MODULES_O) tree_stub.o -L../../../thirdparty/lib -lpoker-eval -o $@

