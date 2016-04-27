#include <stdio.h>
#include <stdlib.h>
#include <unistd.h>
#include <sys/types.h>
#include <sys/stat.h>
#include <fcntl.h>

#define WAIT 60

int main(int argc, char *argv[]) 
{
	/* get current time */
	unsigned int now = (unsigned int)time(NULL);
	unsigned int old_time = 0;
	unsigned int timediff;
	unsigned int time_left;
	int lockfd, res;

	/* get real uid of calling user */
	unsigned int whoami = getuid();

	/* load last time of submitted attack */
	char lockfile[128];
	char lockdata[128];
	sprintf(lockfile, "/var/cctf/attacks/%u.last", whoami);
	if (access(lockfile, F_OK) != -1) {
		/* file exists
		 * http://stackoverflow.com/questions/230062/whats-the-best-way-to-check-if-a-file-exists-in-c-cross-platform */
		if ((lockfd = open(lockfile, O_RDONLY)) < 0) {
			printf("lockfd < 0!\n");
			perror("Couldn't open file:");
			exit(1);
		}

		if ((res = read(lockfd, lockdata, 128)) < 0) {
			printf("read < 0!\n");
			perror("couldn't read file: ");
			exit(1);
		}
		close(lockfd);
		
		old_time = atol(lockdata);
		printf("Old time: %u\n", old_time);
	} else {
		printf("Last time doesn't exist.\n");
	}

	/* if the file doesn't exist, there was no previous time */

	/* find out the difference between old and new times */
	timediff = now - old_time;
	time_left = WAIT - timediff;

	if (timediff >= WAIT) {
		printf("Long enough has passed.\n");
	} else {
		printf("Wait, young grasshopper - %u more seconds.\n", time_left);
	}
	

	printf("Time is: %u\n", now);

}
