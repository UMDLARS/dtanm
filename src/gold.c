#include <ctype.h>
#include <limits.h>
#include <stdbool.h>
#include <stdio.h>
#include <stdlib.h>
#include <string.h>

#define DEBUG 0
#define MAX_TOKEN_LENGTH 7
void error() {
    printf("Error\n");
    exit(1);
}

bool additionOverflow(signed short A, signed short B) {
    if ((A > 0) && (A > SHRT_MAX - B)) return true; /* `A + B` would overflow */;
    if ((A < 0) && (A < SHRT_MIN - B)) return true; /* `A + B` would underflow */;
    return false;
}

bool validChar(char c) {
    int ascii = (int)c;
    //fprintf(stderr, "ascii value %d\n", ascii);
    if (ascii >= 48 && ascii <= 57) { // integers
        return true;
    } else if (ascii == 42 || ascii == 43 || ascii == 45 || ascii == 47) { // operands
        return true;
    } else if (ascii == 44) { // comma
        return true;
    } else if (ascii == 32) { // space
        return true;
    } else {
        return false;
    }
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
    
    if (argc != 2) {  //Exit if more than 2 args
        error();
    }
    
    char *input = argv[1]; //Set input to the chars entered

    char *expression;
    char tokens[3][MAX_TOKEN_LENGTH]; //No instantiation of any of this
    char *curChar;
    signed short A, B, SUM, dividend, quotient, remain, temp, GCD;
    char oper;
    // char tokens[3][42];
    int i, currentToken;

    // Test for blank input
    if (!input[0]) {
        error();
    }
    
    // Test for leading comma
    if (input[0] == ',') {
        if (DEBUG)
            fprintf(stderr, "Error found leading ','\n");
        error();
    }
    
    curChar = input;
    bool prevComma = false;
    while(*curChar) {
        i = 0;
        currentToken = 0;
        while(*curChar != ',' && *curChar) {
            if (!validChar(*curChar)) {
                error();
            }
            if(*curChar == ' '  && i != 0){ // Do not increment if i = 0, removes issue with spaces
                tokens[currentToken][i] = '\0';
                if(currentToken != 2) {
                    i = 0; //2 + 2 , 234234
                    currentToken++;
                }
            }
            else if(*curChar != ' '){
                if(i >= MAX_TOKEN_LENGTH) {
                    error();
                }
                if(DEBUG)
                    fprintf(stderr, "The char to be added to token: %d  %c\n" , currentToken ,*curChar);
                tokens[currentToken][i] = *curChar;
                i++;
            }
            curChar++;
            prevComma = false;
        }
        
        if(currentToken < 2){
            error();
        }
        
        
        if (*curChar == ',') {
            if(prevComma)
                error();
            prevComma = true;
            curChar++;
        }
        if (DEBUG)
            fprintf(stderr,"%d\n", currentToken);
        // curChar++;
        
        tokens[2][i] = '\0';
        if (DEBUG){
            fprintf(stderr, "Token 0 outputs %c\n", *tokens[0]);
            fprintf(stderr, "Token 2 outputs %c\n", *tokens[2]);
        }
        // Check if all tokens are present
        // if (currentToken != 2) {
        //     if (DEBUG)
        //         fprintf(stderr, "Did not get 3 tokens");
        //     error();
        // }
        
        //Assert that tokens are valid
        A = stringToShort(tokens[0]);
        oper = tokens[1][0];
        if (tokens[1][1] != '\0') {
            error();
        }
        B = stringToShort(tokens[2]);
        //End Asserting
        
        
        // Assertion: All tokens are valid
        // Do calculations        
        bool a_negative, b_negative, result_positive;
        switch(oper) {
            case '+':
                if (additionOverflow(A, B)) {
                    error();
                }
                printf("%d\n", (signed short)A+B);
                break;
            case '-':
                if (additionOverflow(A,-B)) {
                    error();
                }
                printf("%d\n", (signed short)A-B);
                break;
            case '*':
                // Should we loop
                a_negative = A < 0;
                b_negative = B < 0;
                A = a_negative ? 0 - A : A;
                B = b_negative ? 0 - B : B;
                result_positive = b_negative == a_negative ? true : false;
                SUM = 0;
                for (i = 0; i < B; i++) {
                    if (additionOverflow(SUM, A)) {
                        error();
                    }
                    SUM += A;
                }
                printf(result_positive ? "%d\n" : "-%d\n", SUM);
                break;
            case '/':
                if(B == 0) {
                    error();
                }
                a_negative = A < 0;
                b_negative = B < 0;
                A = a_negative ? 0 - A : A;
                B = b_negative ? 0 - B : B;
                result_positive = b_negative == a_negative ? true : false;

                
                dividend = A;
                quotient = 0;
                if(DEBUG)
                    fprintf(stderr, "%d\n", dividend);
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
                    printf(result_positive ? "%d\n" : "-%d\n", quotient);
                } else if (quotient == 0) {
                    printf(result_positive ? "%d/%d\n" : "-%d%d\n", remain/GCD, B/GCD);
                } else {
                    printf(result_positive ? "%d %d/%d\n" : "-%d %d/%d\n", quotient, remain/GCD, B/GCD);
                }
                break;
            default:
                // Invalid operator.
                error();
        }
    }
    if(prevComma){
        error(); //Ended on a comma
    }

    return 0;
}