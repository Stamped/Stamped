//
//  STDebug.m
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STDebug.h"
#import "Util.h"

@interface STDebug ()

@property (nonatomic, readonly, retain) NSMutableArray* logs;

@end

@implementation STDebug

@synthesize logs = logs_;

static STDebug* _sharedInstance;

+ (void)initialize {
    _sharedInstance = [[STDebug alloc] init];
}

+ (STDebug*)sharedInstance {
    return _sharedInstance;
}

- (id)init
{
    self = [super init];
    if (self) {
        logs_ = [[NSMutableArray alloc] init];
    }
    return self;
}

- (void)dealloc
{
    [logs_ release];
    [super dealloc];
}

- (void)log:(id)object {
    NSLog(@"%@", object);
    [self.logs addObject:[[[STDebugDatum alloc] initWithObject:object] autorelease]];
}

+ (void)log:(id)object {
    [[STDebug sharedInstance] log:object];
}

- (NSArray*)logSliceWithOffset:(NSInteger)offset andCount:(NSInteger)count {
    if (offset >= self.logs.count) {
        return [NSArray array];
    }
    else {
        NSRange range;
        if (count + offset > self.logs.count) {
            range = NSMakeRange(offset, self.logs.count - offset);
        }
        else {
            range = NSMakeRange(offset, count);
        }
        return [self.logs subarrayWithRange:range];
    }
}

- (STDebugDatum*)logItemAtIndex:(NSInteger)index {
    if (index < self.logCount) {
        return [self.logs objectAtIndex:index];
    }
    else {
        return nil;
    }
}

- (NSInteger)logCount {
    return self.logs.count;
}

@end
