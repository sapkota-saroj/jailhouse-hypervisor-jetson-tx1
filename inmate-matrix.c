/*
 * Jailhouse, a Linux-based partitioning hypervisor
 *
 * Copyright (c) ARM Limited, 2014
 *
 * Authors:
 *  Jean-Philippe Brucker <jean-philippe.brucker@arm.com>
 *
 * This work is licensed under the terms of the GNU GPL, version 2.  See
 * the COPYING file in the top-level directory.
 */

#include <inmate.h>

void inamte_main(void)
{
	unsigned int i = 0, j,k;
	/*
	 * The cell config can set up a mapping to access UARTx instead of UART0
	 */
	/*while(++i) {
		for (j = 0; j < 100000000; j++);
		printk("Hello %d from cell!\n", i);
		heartbeat();
	}*/

	/* lr should be 0, so a return will go back to the reset vector */
int A[][10]={{6252,6378,1000,234,759,5908,2345,7899,1245,5000},{1244,4678,2345,7890,1234,567,2541,9078,4567,8765},{2345,9000,7000,8000,1000,1234,8765,8976,9087,4562},{3232,1212,4343,5454,4545,5656,6565,7676,6767,7878},{8787,8989,9898,9009,7654,4563,7658,7586,8970,3454},{3232,1212,4343,5454,4545,5656,6565,7676,6767,7878},
{2345,9000,7000,8000,1000,1234,8765,8976,9087,4562},{1244,4678,2345,7890,1234,567,2541,9078,4567,8765},{6252,6378,1000,234,759,5908,2345,7899,1245,5000},
{8787,8989,9898,9009,7654,4563,7658,7586,8970,3454}};
int B[][10]={{6252,6378,1000,234,759,5908,2345,7899,1245,5000},{1244,4678,2345,7890,1234,567,2541,9078,4567,8765},{2345,9000,7000,8000,1000,1234,8765,8976,9087,4562},{3232,1212,4343,5454,4545,5656,6565,7676,6767,7878},{8787,8989,9898,9009,7654,4563,7658,7586,8970,3454},{3232,1212,4343,5454,4545,5656,6565,7676,6767,7878},
{2345,9000,7000,8000,1000,1234,8765,8976,9087,4562},{1244,4678,2345,7890,1234,567,2541,9078,4567,8765},{6252,6378,1000,234,759,5908,2345,7899,1245,5000},
{8787,8989,9898,9009,7654,4563,7658,7586,8970,3454}};

int product[10][10];

for(i=0; i<10; i++)
{
	for(j=0; j<10; j++)
	{
		product[i][j]=0;	
		printk("initial matrix [%d][%d]=%d\n", i, j, product[i][j]);
	
	}
}

int sum;

for(i=0; i<10; i++)
{
	for(j=0; j<10; j++)
	{
	sum=0;
		for(k=0; k<10; k++)
		sum+=A[i][k]*B[k][j];
		product[i][j]=sum;
	}
}
//print matrix results:
for(i=0; i<10; i++)
{
	for(j=0; j<10; j++)
		printk("product[%d][%d]=%d\n",i,j,product[i][j]);
usleep(1000000);
}

}
