//
//  STSimpleEntityAutoCompleteResult.m
//  Stamped
//
//  Created by Landon Judkins on 5/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntityAutoCompleteResult.h"

@implementation STSimpleEntityAutoCompleteResult

@synthesize completion = _completion;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _completion = [[decoder decodeObjectForKey:@"completion"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_completion release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.completion forKey:@"completion"];
}

+ (RKObjectMapping*)mapping {
    
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntityAutoCompleteResult class]];
    
    [mapping mapAttributes:@"completion", nil];

    return mapping;
}

@end
