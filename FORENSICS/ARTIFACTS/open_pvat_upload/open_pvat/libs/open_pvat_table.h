/*
	Author: Josh Davidson
	Purpose: To load and lookup pot equities from the table for pvat use
*/
	
#ifndef OPEN_PVAT_TABLE_H
#define OPEN_PVAT_TABLE_H

#include "pvat_defines.h"

int loadPreflopPotEquity();
double lookupPreflopPotEquity(int* cards0, int* cards1);

#endif
