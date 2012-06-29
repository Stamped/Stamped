//
//  STSimpleLinkedAccounts.m
//  Stamped
//
//  Created by Landon Judkins on 6/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STSimpleLinkedAccounts.h"
#import "STSimpleLinkedAccount.h"

@implementation STSimpleLinkedAccounts

@synthesize facebook = _facebook;
@synthesize twitter = _twitter;
@synthesize rdio = _rdio;
@synthesize spotify = _spotify;
@synthesize netflix = _netflix;

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _facebook = [[decoder decodeObjectForKey:@"facebook"] retain];
        _twitter = [[decoder decodeObjectForKey:@"twitter"] retain];
        _rdio = [[decoder decodeObjectForKey:@"rdio"] retain];
        _spotify = [[decoder decodeObjectForKey:@"spotify"] retain];
        _netflix = [[decoder decodeObjectForKey:@"netflix"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_facebook release];
    [_twitter release];
    [_rdio release];
    [_spotify release];
    [_netflix release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.facebook forKey:@"facebook"];
    [encoder encodeObject:self.twitter forKey:@"twitter"];
    [encoder encodeObject:self.rdio forKey:@"rdio"];
    [encoder encodeObject:self.spotify forKey:@"spotify"];
    [encoder encodeObject:self.netflix forKey:@"netflix"];
}


+ (RKObjectMapping*)mapping {
    RKObjectMapping* mapping = [RKObjectMapping mappingForClass:self];
    
    for (NSString* name in [NSArray arrayWithObjects:@"facebook", @"twitter", @"rdio", @"spotify", @"netflix", nil]) {
        [mapping mapRelationship:name withMapping:[STSimpleLinkedAccount mapping]];
    }
    
    return mapping;
}

@end
