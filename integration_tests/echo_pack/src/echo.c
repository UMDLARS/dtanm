#include <stdio.h>
#include <string.h>

int main (int argc, char** argv) {
	char buffer[32];
	char* ptr = buffer;
	for (int i = 0; i < sizeof(buffer); i++)
		buffer[i] = 0;
	for (int i = 1; i < argc; i++) {
		strcpy(ptr, argv[i]); // Copy the argument to the buffer
		ptr += strlen(argv[i]); // Increment through the buffer
		if (i < argc - 1) { // not the last argument -- dont't want a trailing space!
			*ptr = ' '; // Add a space between arguments
			ptr++;
		}
	}
	printf("%s\n", buffer); // print out all the arguments
	return 0;
}
