#include <stdio.h> 
#include <stdlib.h> 
#include <string.h> 
#include <fcntl.h> 
#include <sys/shm.h> 
#include <unistd.h>
#include <sys/stat.h>
#include <sys/mman.h>
#define MEM_SIZE 0x10000 
int main()
{
	void* mapped_base;
	void* mapped_dev_base;
	int memfd;
	//char str[]="hello";

	memfd = open("/dev/mem", O_RDWR | O_SYNC);
	if (memfd<0){
		printf("can't open file, existing...\n");
		exit(-1);
	}
	mapped_base = mmap((void*)0x17ba00000, MEM_SIZE, PROT_READ | PROT_WRITE, MAP_SHARED, memfd, 0); // & ~MEM_MASK);
	if (mapped_base == MAP_FAILED) {
		close(memfd);
		perror("Error mmapping the file");
		exit(EXIT_FAILURE);
	}
	//strcpy((char*)mapped_base,str);

	mapped_dev_base = mapped_base; //+ (dev_base & MEM_MASK);
	printf("test \n");
	for(int i = 4; i < 12; i += 4) {
       // *((volatile unsigned int *) (mapped_dev_base + i)) = 12;
        printf("Address: %p, Read valeu = %d\n", (void *)(mapped_dev_base + i), *((unsigned int *) (mapped_dev_base + i)));
		}
	 if (munmap(mapped_base, MEM_SIZE) == -1) {
		perror("Error un-mmapping the file");
	}
	close(memfd);
	return 0;
}
