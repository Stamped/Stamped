//
//  STSimpleBooleanResponse.m
//  Stamped
//
//  Created by Landon Judkins on 6/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleBooleanResponse.h"

@implementation STSimpleBooleanResponse

@synthesize result = _result;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _result = [[decoder decodeObjectForKey:@"result"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_result release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.result forKey:@"result"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapAttributes:@"result", nil];
    
    return mapping;
}

@end
