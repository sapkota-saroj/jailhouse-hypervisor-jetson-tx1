#include <stdio.h>
#include <stdlib.h>
#include <time.h>
//#define N 20

void getmatrix(int row, int column, int a[row][column])
{
        unsigned int i,j;
        for(i=0;i<row;i++)
        {
                for (j=0; j<column;j++)
                {
                        a[i][j]=rand()%100;
                }
        }
}
void printmatrix(int row, int column, int a[row][column])
{
        unsigned int i,j;
        for(i=0;i<row;i++)
        {
                for (j=0; j<column;j++)
                {
                        printf("matrix[%d][%d]=%d\n",i,j,a[i][j]);
                }
        }
}
void initialize(int row, int column, int a[row][column])
{
        unsigned int i,j;
        for (i=0;i<row;i++)
        {
                for (j=0;j<column;j++)
                {
                         a[i][j]=0;
                }
        }

}

int main(int argc,char *argv[])
{
        clock_t begin=clock();
        unsigned int row, column, i, j, k; //select=0;
        if(argv[1]==NULL)
        {
                      row=2;
                column=2;
        }
        else if(argv[1]!=NULL && argv[2]==NULL)
        {
                row=column=atoi(argv[1]);
        }
        else
        {
                row=atoi(argv[1]);
                column=atoi(argv[2]);
        }
        int A[row][column];
        int B[column][row];
        int C[row][row];
        initialize(row,column,A);
        getmatrix(row,column,A);
        //printmatrix(row,column,A);
        initialize(column,row,B);
        getmatrix(column,row,B);
        //printmatrix(column,row,B);
        initialize(row,row,C);
        for (i=0;i<row;i++)
        {
                for (j=0;j<column;j++)
                {     //if (select==1)
                                //{
                                        C[i][j]+=A[i][k]*B[k][j];
                                //}
                                /*else
                                {
                                        C[i][j]+=A[k][i]*B[j][k];
                                } */

                }
        }
        printmatrix(row,row,C);
        clock_t end=clock();
        double time_spent= (double)(end-begin)/CLOCKS_PER_SEC;
        printf("excution time is %f \n", time_spent);
        return 0;

}

