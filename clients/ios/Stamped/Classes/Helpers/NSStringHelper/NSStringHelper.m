//
//  NSStringHelper.m
//  Stamped
//
//  Created by Devin Doty on 6/15/12.
//
//

#import "NSStringHelper.h"

@implementation NSString (Helper)

+ (NSString *)ordinalString:(NSNumber *)rank {
    
    NSString *suffix = nil;
    int rankInt = [rank intValue];
    int ones = rankInt % 10;
    int tens = floor(rankInt / 10);
    tens = tens % 10;
    if (tens == 1) {
        suffix = @"th";
    } else {
        switch (ones) {
            case 1 : suffix = @"st"; break;
            case 2 : suffix = @"nd"; break;
            case 3 : suffix = @"rd"; break;
            default : suffix = @"th";
        }
    }
    NSString *rankString = [NSString stringWithFormat:@"%@%@", rank, suffix];
    return rankString;
    
}

@end
