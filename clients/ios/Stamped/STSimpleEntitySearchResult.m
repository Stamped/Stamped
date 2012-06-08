//
//  STSimpleEntitySearchResult.m
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleEntitySearchResult.h"

@implementation STSimpleEntitySearchResult

@synthesize searchID = searchID_;
@synthesize title = title_;
@synthesize subtitle = subtitle_;
@synthesize category = category_;
@synthesize distance = distance_;
@synthesize icon = icon_;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        searchID_ = [[decoder decodeObjectForKey:@"searchID"] retain];
        title_ = [[decoder decodeObjectForKey:@"title"] retain];
        subtitle_ = [[decoder decodeObjectForKey:@"subtitle"] retain];
        category_ = [[decoder decodeObjectForKey:@"category"] retain];
        distance_ = [[decoder decodeObjectForKey:@"distance"] retain];
        icon_ = [[decoder decodeObjectForKey:@"icon"] retain];
    }
    return self;
}

- (void)dealloc
{
    [searchID_ release];
    [title_ release];
    [subtitle_ release];
    [category_ release];
    [distance_ release];
    [icon_ release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.searchID forKey:@"searchID"];
    [encoder encodeObject:self.title forKey:@"title"];
    [encoder encodeObject:self.subtitle forKey:@"subtitle"];
    [encoder encodeObject:self.category forKey:@"category"];
    [encoder encodeObject:self.distance forKey:@"distance"];
    [encoder encodeObject:self.icon forKey:@"icon"];
}

+ (RKObjectMapping *)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:[STSimpleEntitySearchResult class]];
    
    [mapping mapAttributes:
     @"title",
     @"subtitle",
     @"category",
     @"distance",
     @"icon",
     nil];
    
    [mapping mapKeyPathsToAttributes:@"search_id", @"searchID", nil];
    
    return mapping;
}

@end
