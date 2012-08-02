//
//  STSimpleActivityCount.m
//  Stamped
//
//  Created by Landon Judkins on 5/8/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleActivityCount.h"
#import "STSimpleAction.h"

@implementation STSimpleActivityCount

@synthesize numberUnread = numberUnread_;
@synthesize action = _action;

- (id)initWithCoder:(NSCoder *)decoder
{
    self = [super init];
    if (self) {
        numberUnread_ = [[decoder decodeObjectForKey:@"numberUnread"] retain];
        _action = [[decoder decodeObjectForKey:@"action"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_action release];
    [numberUnread_ release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.numberUnread forKey:@"numberUnread"];
    [encoder encodeObject:self.action forKey:@"action"];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleActivityCount class]];
    
    [mapping mapKeyPathsToAttributes: 
     @"num_unread", @"numberUnread",
     nil];
    
    [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
    
    return mapping;
}

@end
