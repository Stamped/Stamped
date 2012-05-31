//
//  STSimpleStampPreview.m
//  Stamped
//
//  Created by Landon Judkins on 5/31/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleStampPreview.h"
#import "STSimpleUser.h"

@implementation STSimpleStampPreview

@synthesize stampID = _stampID;
@synthesize user = _user;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _stampID = [[decoder decodeObjectForKey:@"stampID"] retain];
        _user = [[decoder decodeObjectForKey:@"user"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_stampID release];
    [_user release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.stampID forKey:@"stampID"];
    [encoder encodeObject:self.user forKey:@"user"];
}

+ (RKObjectMapping*)mapping {
    
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    [mapping mapKeyPath:@"stamp_id" toAttribute:@"stampID"];
    
    [mapping mapRelationship:@"user" withMapping:[STSimpleUser mapping]];
    
    return mapping;
}
@end
