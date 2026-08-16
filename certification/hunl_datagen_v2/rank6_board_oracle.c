#include <stdio.h>
#include <stdint.h>
#include <stdlib.h>
#include "game.h"

static inline void add_acpc(Cardset *c, int id) {
    int rank = id / 4;
    int suit = id % 4;
    addCardToCardset(c, suit, rank);
}

int main(int argc, char **argv) {
    if (argc != 5) {
        fprintf(stderr, "usage: %s b0 b1 b2 b3\n", argv[0]);
        return 2;
    }
    int b[4];
    for (int i=0;i<4;i++) b[i]=atoi(argv[i+1]);
    for (int i=0;i<4;i++) for (int j=i+1;j<4;j++) if (b[i]==b[j]) return 3;
    for (int c0=0;c0<52;c0++) {
        for (int c1=c0+1;c1<52;c1++) {
            int blocked=0;
            for (int k=0;k<4;k++) if (c0==b[k] || c1==b[k]) blocked=1;
            int32_t r=-1;
            if (!blocked) {
                Cardset cs=emptyCardset();
                add_acpc(&cs,c0); add_acpc(&cs,c1);
                for (int k=0;k<4;k++) add_acpc(&cs,b[k]);
                r=(int32_t)rankCardset(cs);
            }
            if (fwrite(&r,sizeof(r),1,stdout)!=1) return 4;
        }
    }
    return 0;
}
