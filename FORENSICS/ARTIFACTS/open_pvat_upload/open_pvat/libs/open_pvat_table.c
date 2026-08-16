#include "open_pvat_table.h"

double equity_table[DECK_SIZE][DECK_SIZE][DECK_SIZE][DECK_SIZE];

int loadPreflopPotEquity()
{
	int i,j,k,l;
	double equity;
	FILE *f;
	char line[256];
	/*Initialize the table to -1*/
	for(i=0;i<DECK_SIZE;i++) {
		for(j=0;i<DECK_SIZE;i++) {
			for(k=0;i<DECK_SIZE;i++) {
				for(l=0;i<DECK_SIZE;i++) {
					equity_table[i][j][k][l] = -1;
				}
			}
		}
	}
	/*Load in the file*/
  fprintf( stderr, "Loading preflop pot equity table...");
  f = fopen("preflopPotEquityTable.table","r");
	while(!feof(f)) {
		fgets(line,sizeof(line),f);
		if(sscanf(line,"(%d,%d,%d,%d):%lf",&i,&j,&k,&l,&equity)) {
			equity_table[i][j][k][l] = equity;
		} else {
			fprintf(stderr,"failed\nexiting...\n");
			exit(-1);
		}
	}
	fclose(f);
	fprintf(stderr, "sucess\n");
	return 0;
}

double lookupPreflopPotEquity(int* cards0, int* cards1)
{
	int pocketcards[4];
	double equity;

  pocketcards[0] = cards0[0];
  pocketcards[1] = cards0[1];
  pocketcards[2] = cards1[0];
  pocketcards[3] = cards1[1];

	//Sort the cards proper
	if(pocketcards[0] > pocketcards[1]) {
		pocketcards[0] = cards0[1];
		pocketcards[1] = cards0[0];
	}

	if(pocketcards[2] > pocketcards[3]) {
		pocketcards[2] = cards1[1];
		pocketcards[3] = cards1[0];
	}

	equity = equity_table[pocketcards[0]][pocketcards[1]][pocketcards[2]][pocketcards[3]];
	return equity;
}

