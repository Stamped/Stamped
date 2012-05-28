//
//  STSimpleEntitySearchSection.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntitySearchSection.h"
#import "STSimpleEntitySearchResult.h"

@implementation STSimpleEntitySearchSection

@synthesize title = _title;
@synthesize subtitle = _subtitle;
@synthesize imageURL = _imageURL;
@synthesize entities = _entities;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _title = [[decoder decodeObjectForKey:@"title"] retain];
        _subtitle = [[decoder decodeObjectForKey:@"subtitle"] retain];
        _imageURL = [[decoder decodeObjectForKey:@"imageURL"] retain];
        _entities = [[decoder decodeObjectForKey:@"entities"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_title release];
    [_subtitle release];
    [_imageURL release];
    [_entities release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.title forKey:@"title"];
    [encoder encodeObject:self.subtitle forKey:@"subtitle"];
    [encoder encodeObject:self.imageURL forKey:@"imageURL"];
    [encoder encodeObject:self.entities forKey:@"entities"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntitySearchSection class]];
    
    [mapping mapAttributes:
     @"title",
     @"subtitle",
     @"imageURL",
     nil];
    
    [mapping mapRelationship:@"entities" withMapping:[STSimpleEntitySearchResult mapping]];
    
    return mapping;
}

@end
