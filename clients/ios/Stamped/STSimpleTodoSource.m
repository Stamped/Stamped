//
//  STSimpleTodoSource.m
//  Stamped
//
//  Created by Landon Judkins on 5/22/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleTodoSource.h"
#import "STSimpleEntity.h"

@implementation STSimpleTodoSource

@synthesize entity = _entity;
@synthesize stampIDs = _stampIDs;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _entity = [[decoder decodeObjectForKey:@"entity"] retain];
        _stampIDs = [[decoder decodeObjectForKey:@"stamp"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_entity release];
    [_stampIDs release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.entity forKey:@"entity"];
    [encoder encodeObject:self.stampIDs forKey:@"stampIDs"];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleTodoSource class]];
    
    [mapping mapKeyPathsToAttributes:
     @"stamp_ids",@"stampIDs",
     nil];
    
    [mapping mapRelationship:@"entity" withMapping:[STSimpleEntity mapping]];
    
    return mapping;
}

@end
