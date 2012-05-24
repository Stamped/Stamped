//
//  STSimpleTodo.m
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleTodo.h"
#import "STSimpleTodoSource.h"
#import "STSimplePreviews.h"
#import "STSimpleEntity.h"

@implementation STSimpleTodo

@synthesize todoID = _todoID;
@synthesize userID = _userID;
@synthesize created = _created;
@synthesize complete = _complete;
@synthesize stampID = _stampID;
@synthesize source = _source;
@synthesize previews = _previews;

//TODO remove
@synthesize entity = _entity;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _todoID = [[decoder decodeObjectForKey:@"todoID"] retain];
        _userID = [[decoder decodeObjectForKey:@"userID"] retain];
        _created = [[decoder decodeObjectForKey:@"created"] retain];
        _complete = [[decoder decodeObjectForKey:@"complete"] retain];
        _source = [[decoder decodeObjectForKey:@"source"] retain];
        _stampID = [[decoder decodeObjectForKey:@"stampID"] retain];
        _previews = [[decoder decodeObjectForKey:@"previews"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_todoID release];
    [_userID release];
    [_created release];
    [_complete release];
    [_source release];
    [_stampID release];
    [_previews release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.todoID forKey:@"todoID"];
    [encoder encodeObject:self.userID forKey:@"userID"];
    [encoder encodeObject:self.created forKey:@"created"];
    [encoder encodeObject:self.complete forKey:@"complete"];
    [encoder encodeObject:self.source forKey:@"source"];
    [encoder encodeObject:self.stampID forKey:@"stampID"];
    [encoder encodeObject:self.previews forKey:@"previews"];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleTodo class]];
    
    [mapping mapKeyPathsToAttributes:
     @"favorite_id", @"todoID",
     @"user_id", @"userID",
     @"stamp_id", @"stampID",
     nil];
    
    [mapping mapAttributes:
     @"created",
     @"complete",
     nil];
    
    [mapping mapRelationship:@"source" withMapping:[STSimpleTodoSource mapping]];
    [mapping mapRelationship:@"previews" withMapping:[STSimplePreviews mapping]];
    //TODO remove
    [mapping mapRelationship:@"entity" withMapping:[STSimpleEntity mapping]];
    
    return mapping;
}

@end
