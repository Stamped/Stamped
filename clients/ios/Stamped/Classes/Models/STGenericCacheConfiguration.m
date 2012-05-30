//
//  STGenericCacheConfiguration.m
//  Stamped
//
//  Created by Landon Judkins on 5/27/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCacheConfiguration.h"
#import "Util.h"

@implementation STGenericCacheConfiguration

@synthesize pageSource = _pageSource;
@synthesize directory = _directory;
@synthesize pageFaultAge = _pageFaultAge;
@synthesize preferredPageSize = _preferredPageSize;
@synthesize minimumPageSize = _minimumPageSize;

- (id)init {
    self = [super init];
    if (self) {
        _pageSource = nil;
        _directory = [[Util cacheDirectory] copy];
        NSLog(@"Cache dir: %@", _directory);
        _pageFaultAge = 1 * 24 * 60 * 60;
        _preferredPageSize = 20;
        _minimumPageSize = 20;
    }
    return self;
}

- (void)dealloc
{
    [_pageSource release];
    [_directory release];
    [super dealloc];
}

@end

