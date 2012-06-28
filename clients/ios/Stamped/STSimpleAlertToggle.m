//
//  STSimpleAlertToggle.m
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleAlertToggle.h"

@implementation STSimpleAlertToggle

@synthesize toggleID = _toggleID;
@synthesize type = _type;
@synthesize value = _value;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _toggleID = [[decoder decodeObjectForKey:@"toggleID"] retain];
        _type = [[decoder decodeObjectForKey:@"type"] retain];
        _value = [[decoder decodeObjectForKey:@"value"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_toggleID release];
    [_type release];
    [_value release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.toggleID forKey:@"toggleID"];
    [encoder encodeObject:self.type forKey:@"type"];
    [encoder encodeObject:self.value forKey:@"value"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapKeyPathsToAttributes:
     @"toggle_id", @"toggleID",
     @"type", @"type",
     @"value", @"value",
     nil];
    
    return mapping;
}

@end
