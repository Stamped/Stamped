//
//  STSimplePlaylistItem.m
//  Stamped
//
//  Created by Landon Judkins on 3/7/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimplePlaylistItem.h"
#import "STSimpleSource.h"
#import "STSimpleAction.h"
#import "STSimpleImage.h"

@implementation STSimplePlaylistItem

@synthesize name = name_;
@synthesize subtitle = _subtitle;
@synthesize length = length_;
@synthesize icon = icon_;
@synthesize entityID = _entityID;
@synthesize images = _images;
@synthesize action = action_;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        name_ = [[decoder decodeObjectForKey:@"name"] retain];
        _subtitle = [[decoder decodeObjectForKey:@"subtitle"] retain];
        length_ = [decoder decodeIntegerForKey:@"length"];
        icon_ = [[decoder decodeObjectForKey:@"icon"] retain];
        _entityID = [[decoder decodeObjectForKey:@"entityID"] retain];
        _images = [[decoder decodeObjectForKey:@"images"] retain];
        action_ = [[decoder decodeObjectForKey:@"action"] retain];
    }
    return self;
}

- (void)dealloc {
    self.name = nil;
    self.icon = nil;
    self.action = nil;
    self.entityID = nil;
    [_subtitle release];
    [_images release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.name forKey:@"name"];
    [encoder encodeObject:self.subtitle forKey:@"subtitle"];
    [encoder encodeInteger:self.length forKey:@"length"];
    [encoder encodeObject:self.icon forKey:@"icon"];
    [encoder encodeObject:self.action forKey:@"action"];
    [encoder encodeObject:self.entityID forKey:@"entityID"];
    [encoder encodeObject:self.images forKey:@"images"];
}

+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimplePlaylistItem class]];
    
    [mapping mapAttributes:
     @"subtitle",
     @"name",
     @"icon",
     @"length",
     nil];
    
    [mapping mapKeyPathsToAttributes:@"entity_id", @"entityID", nil];
    
    [mapping mapRelationship:@"action" withMapping:[STSimpleAction mapping]];
    [mapping mapRelationship:@"images" withMapping:[STSimpleImage mapping]];
    
    return mapping;
}

+ (STSimplePlaylistItem*)playlistItemWithItem:(id<STPlaylistItem>)item {
    NSData* data = [NSKeyedArchiver archivedDataWithRootObject:item];
    return [NSKeyedUnarchiver unarchiveObjectWithData:data];
}

@end
