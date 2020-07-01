#include <inmate.h>
#define SIZE 15

void mat_init(long int row, long int col, long int mat[row][col]);
void mat_print(long int row, long int col, long int mat[row][col]);
void mat_mul(long int row, long int col, long int mat[row][col],long int A[row][col],long int B[row][col]);

void mat_init(long int row, long int col, long int mat[row][col])
{
        long int i, j;
        for (i=0; i<row; i++)
        {
                for (j=0; j<row; j++)
                        mat[i][j]=0;
        }
}

void mat_print(long int row, long int col, long int mat[row][col])
{
        long int i, j;
        for (i=0; i<row; i++)
        {
                for (j=0; j<col; j++)

                        printk("mat[%ld][%ld]=%ld \n",i,j,mat[i][j]);

        }
}

void mat_mul(long int row, long int col, long int mat[row][col],long int A[row][col],long int B[row][col])
{
        long int i,j,k;
          for(i=0; i<row; i++)
        {
                for(j=0; j<col; j++)
                {
//                      mat[i][j]=0;
                        for(k=0; k<col; k++){
                                mat[i][j]+=A[i][k]*B[k][j];
                        }
                }
        }
//      mat_print(row,col,mat);

}

