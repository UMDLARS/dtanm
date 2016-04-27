#include <ctype.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEBUG 0

void error() {
    printf("Error\n");
    exit(1);
}

signed short stringToShort(char *s) {
    if (DEBUG)
        fprintf(stderr, "Parsing String for Short\n");
    // Check if valid integer
    char *str = s;

    // if negative skip '-' sign
    if (*str == '-') {
        ++str;
    }
    
    // if empty string or just "-" throw error.
    if (!*str) {
        if (DEBUG)
            fprintf(stderr, "Error parsing String: empty string or just '-'\n");
        error();
    }
    
    // If any of the other characters are not digits then throw an error.
    while (*str)
    {
        if (!isdigit(*str)) {
            if (DEBUG)
                fprintf(stderr, "Error parsing String: found non digit.\n");
            error();
        }
        else {
            ++str;
        }
    }
    
    char *pEnd;
    long int tmp = strtol(s, &pEnd, 10);
    
    // if error parsing
    if (pEnd == NULL) {
        if (DEBUG)
            fprintf(stderr, "Error parsing String: error in strtol.\n");
        error();
    }
    
    if (DEBUG)
        fprintf(stderr, "Result: %ld\n", tmp);
    
    if ((long int)SHRT_MIN <= tmp && tmp <= SHRT_MAX) {
        return (signed short)tmp;
    } else {
        error();
    }
}

int main(int argc, char *argv[]) {
    
    //TODO: check if there are enough args
    
    char *input = argv[1];

    //TODO: Remove these fixed sizes
    char *expression, *token;
    char *saveptr1, *saveptr2;
    signed short A, B, SUM, dividend, quotient, remain, temp, GCD;
    char oper;
    int i;
    
    
    // Test for leading comma
    if (input[0] == ',') {
        if (DEBUG)
            fprintf(stderr, "Error found leading ','\n");
        error();
    }
    
    for (expression = strtok_r(input, ",", &saveptr1); expression; expression = strtok_r(NULL, ",", &saveptr1)) {
        if (DEBUG)
            fprintf(stderr, "'%c' '%c' '%c' '%c'\n", *(saveptr1-1), *saveptr1, *(saveptr1+1), *(saveptr1+2));
        if (DEBUG)
            fprintf(stderr, "Expression: %s\n", expression);
        // Get input
        
        bool gotall = false;
        for (i = 0, token = strtok(expression, " "); token; token = strtok(NULL, " "), i++) {
            if (DEBUG)
                fprintf(stderr, "\tToken: %s\n", token);
            switch (i) {
                case 0:
                    A = stringToShort(token);
                    break;
                case 1:
                    oper = token[0];
                    break;
                case 2:
                    B = stringToShort(token);
                    gotall = true;
                    break;
                default:
                    // Exit in the case you get more than 3 tokens.
                    error();
            }
        }
        
        // If we got less than 3 tokens
        if (!gotall) {
            if (DEBUG)
                fprintf(stderr, "Did not get 3 tokens");
            error();
        }
        
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
                SUM = 0;
                for (i = 0; i < B; i++) {
                    SUM += A;
                }
                printf("%d\n", SUM);
                break;
            case '/':
                dividend = A;
                quotient = 0;
                while (dividend >= B) {
                    dividend -= B;
                    quotient++;
                }
                
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
            default:
                // Invalid operator.
                error();
        }
        
        // test to see if we have a double comma
        if (*saveptr1 == ',') {
            error();
        }
        // test for trailing comma
        if (!*(saveptr1-1) && !*saveptr1) {
            error();
        }
    }

    return 0;
}