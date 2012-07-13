//
//  STObjectSetAccellerator.m
//  Stamped
//
//  Created by Landon Judkins on 7/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STObjectSetAccelerator.h"

@interface STObjectSetAccelerator ()

@property (nonatomic, readonly, retain) NSDictionary* keysToDatums;

@end

@implementation STObjectSetAccelerator

@synthesize keysToDatums = _keysToDatums;

+ (id<STCacheAccelerator>)acceleratorForObjects:(NSArray<STDatum>*)objects {
    return [[[STObjectSetAccelerator alloc] initWithObjects:objects] autorelease];
}

- (id)initWithObjects:(NSArray<STDatum>*)objects {
    self = [super init];
    if (self) {
        NSMutableDictionary* m = [NSMutableDictionary dictionary];
        for (id<STDatum> datum in objects) {
            [m setObject:datum forKey:datum.key];
        }
        _keysToDatums = [m retain];
    }
    return self;
}

- (id<STDatum>)datumForCurrentDatum:(id<STDatum>)datum {
    return [self.keysToDatums objectForKey:datum.key];
}
             

@end
