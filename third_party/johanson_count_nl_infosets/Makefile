CFLAGS = -O3 -Wall
INCLUDE = 
LIBS = -lgmp


all: count_nl_infosets count_limit_infosets

clean:
	rm count_nl_infosets count_limit_infosets *~

count_nl_infosets: count_nl_infosets.c constants.h constants.c utility.h utility.c
	gcc $(CFLAGS) $(INCLUDE) $(LIBS) count_nl_infosets.c constants.c utility.c -o count_nl_infosets

count_limit_infosets: count_limit_infosets.c constants.h constants.c utility.h utility.c
	gcc $(CFLAGS) $(INCLUDE) $(LIBS) count_limit_infosets.c constants.c utility.c -o count_limit_infosets
