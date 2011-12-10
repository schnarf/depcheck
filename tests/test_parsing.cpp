#include <iostream>
//#include <cmath>
#include "some_header.h"
   	#include "still_included.h"
   		#include <also_included>
#ifdef 0
	#include <also_included.h>
//#include "not_included.h"
#endif #include <not_included.h>

int main( int argc, char* argv ) {
	return 0;
}
