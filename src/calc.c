/* (c) Dingwall Inc. 
 * authors: Lord Dingwall, Sleepy Joe, Sir Napsalot
 */

#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void error() {
    printf("Error\n");
    exit(1);
}

int main(int argc, char *argv[]) {

    char *input = argv[1];

    char tokens[3][42];
    char *curChar;
    signed short A, B, SUM, dividend, quotient, remain, temp, GCD;
    char oper;
    int i;
    int currentToken;

    for(i = 0; i < 3; i++) {
        for(int n = 0; n < 42; n++) {
            tokens[i][n] = 0;
        }
    }

    curChar = input;
    printf("%s", curChar);
    while(*curChar) {
        i = 0;
        currentToken = 0;
        while(*curChar != ',' && *curChar) {
            if (*curChar == ' ') {
                currentToken++;
                i = 0;
            } else {
                tokens[currentToken][i] = *curChar;
                i++;
            }
            curChar++;
        }
        tokens[2][i] = '\0';
        
        
        A = atoi(tokens[0]);
        oper = tokens[1][0];
        B = atoi(tokens[2]);
        
        // Do calculations
        switch(oper) {
            case '+':
                printf("%d\n", A+B);
                break;
            case '-':
                printf("%d\n", A-B);
                break;
            case '*':
                // Should we loop
                SUM = B;
                for (i = 1; i < B; i++) {
                    SUM += A;
                }
                printf("%d\n", SUM);
                break;
            case '/':
                dividend = A;
                quotient = 0;
                while (dividend > B) {
                    dividend -= B;
                    quotient++;
                }
                
                // GCD calculation to reduce fraction
                GCD = B;
                remain = dividend;
                
                // dividend is the remainder
                while (dividend != 0) {
                    temp = dividend;
                    dividend = GCD % dividend;
                    GCD = temp;
                }
                
                if (remain == 0) {
                    printf("%d\n", quotient);
                } else if (quotient == 0) {
                    printf("%d/%d\n", remain/GCD, B/GCD);
                } else {
                    printf("%d %d/%d\n", quotient, remain/GCD, B/GCD);
                }
                break;
        }
        if (*curChar) {
            curChar++;
        }
    }
    return 0;
}