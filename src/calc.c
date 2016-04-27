#include <stdio.h>
#include <stdlib.h>
#include <string.h>

void error() {
    printf("Error\n");
    exit(1);
}

int main(int argc, char *argv[]) {

    char *input = argv[1];

    char *expression, *token;
    char *tokens[3];
    char *saveptr1;
    signed short A, B, SUM, dividend, quotient, remain, temp, GCD;
    char oper;
    int i;

    for (expression = strtok_r(input, ",", &saveptr1); expression; expression = strtok_r(NULL, ",", &saveptr1)) {
        // Get input
        for (i = 0, token = strtok(expression, " "); token; token = strtok(NULL, " "), i++) {
            tokens[i] = token;
        }
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
                SUM = B; //REMOVE THIS: this should be 0 and i should = 0
                for (i = 1; i < B; i++) {
                    SUM += A;
                }
                printf("%d\n", SUM);
                break;
            case '/':
            
                //REMOVE THIS: This has an off by one error currently
                dividend = A;
                quotient = 0;
                while (dividend > B) { //REMOVE THIS: > should be >=
                    dividend -= B;
                    quotient++;
                }
                
                // GCD calculation to reduce fraction
                //REMOVE THIS: change this to be more buggy
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
    }
    
    return 0;
}