// Copyright 2015 Google Inc. All rights reserved.
//
// Licensed under the Apache License, Version 2.0 (the "License");
// you may not use this file except in compliance with the License.
// You may obtain a copy of the License at
//
//     http://www.apache.org/licenses/LICENSE-2.0
//
// Unless required by applicable law or agreed to in writing, software
// distributed under the License is distributed on an "AS IS" BASIS,
// WITHOUT WARRANTIES OR CONDITIONS OF ANY KIND, either express or implied.
// See the License for the specific language governing permissions and
// limitations under the License.

//
// sample code based on:
// http://stackoverflow.com/questions/9244481/how-to-get-100-cpu-usage-from-a-c-program
//

#include <stdio.h>
#include <time.h>
int main(int argc, char **argv)
{
	int failure = 0;
	if (argc != 2) {
		printf("Usage: primes <max up to 2^31>\n");
		failure = 1;
	} else {
		clock_t start, end;
		double runTime;
		start = clock();
		int i, num = 1, primes = 0;
		int max = atoi(argv[1]);
		while (num <= max) {
			i = 2;
			while (i <= num) {
				if (num % i == 0)
					break;
				i++;
			}
			if (i == num)
				primes++;
			num++;
		}
		end = clock();
		runTime = (end - start) / (double)CLOCKS_PER_SEC;
		printf
		    ("This machine calculated all %d prime numbers under %d in %g seconds\n",
		     primes, max, runTime);
	}
	return failure;
}
