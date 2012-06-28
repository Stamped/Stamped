//
//  STSimpleAlertItem.m
//  Stamped
//
//  Created by Landon Judkins on 6/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleAlertItem.h"
#import "STSimpleAlertToggle.h"

@implementation STSimpleAlertItem

@synthesize groupID = _groupID;
@synthesize name = _name;
@synthesize toggles = _toggles;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _groupID = [[decoder decodeObjectForKey:@"groupID"] retain];
        _name = [[decoder decodeObjectForKey:@"name"] retain];
        _toggles = [[decoder decodeObjectForKey:@"toggles"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_groupID release];
    [_name release];
    [_toggles release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.groupID forKey:@"groupID"];
    [encoder encodeObject:self.name forKey:@"name"];
    [encoder encodeObject:self.toggles forKey:@"toggles"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];

    [mapping mapKeyPathsToAttributes:
     @"group_id", @"groupID",
     @"name", @"name",
     nil];
    
    [mapping mapRelationship:@"toggles" withMapping:[STSimpleAlertToggle mapping]];
    
    return mapping;
}

@end
