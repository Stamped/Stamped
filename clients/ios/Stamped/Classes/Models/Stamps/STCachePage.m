//
//  STCachePage.m
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCachePage.h"

@interface STCachePage ()

@property (nonatomic, readonly, retain) NSDictionary* localIndicesByKey;
@property (nonatomic, readonly, retain) NSArray<STDatum>* localObjects;
@property (nonatomic, readonly, assign) NSInteger nextOffset;
//- (NSArray<STDatum>*)localObjectsAfterDate:(NSDate*)date;

@end

@implementation STCachePage

@synthesize localObjects = _localObjects;
@synthesize localIndicesByKey = _localIndicesByKey;
@synthesize start = _start;
@synthesize end = _end;
@synthesize next = _next;
@synthesize nextOffset = _nextOffset;
@synthesize count = _count;

- (id)init {
    NSAssert1(NO, @"Tried to init() a STCachePage (%@), use initWithObjects:...", self);
    return nil;
}

- (id)initWithObjects:(NSArray<STDatum>*)objects 
                start:(NSDate*)start 
                  end:(NSDate*)end 
              andNext:(STCachePage*)next {
    self = [super init];
    if (self) {
        //TODO ensure sorted, with order preservation
        NSAssert1(objects != nil, @"Objects must not be nil for %@", self);
        _localObjects = [[NSArray arrayWithArray:objects] retain];
        NSMutableDictionary* indices = [NSMutableDictionary dictionary];
        NSDate* replacementEnd = nil;
        for (NSInteger i = 0; i < _localObjects.count; i++) {
            NSNumber* index = [NSNumber numberWithInteger:i];
            id<STDatum> datum = [_localObjects objectAtIndex:i];
            [indices setObject:index forKey:datum.key];
            if (!end) {
                if (replacementEnd) {
                    replacementEnd = [datum.timestamp earlierDate:replacementEnd];
                }
                else {
                    replacementEnd = datum.timestamp;
                }
            }
        }
        _localIndicesByKey = [[NSDictionary dictionaryWithDictionary:indices] retain];
        NSAssert1(start != nil, @"Start date must not be nil for %@", self);
        _start = [start retain];
        if (!end) {
            end = replacementEnd;
        }
        _end = [end retain];
        NSNumber* endIndex = [next indexAfterDate:_end];
        if (endIndex) {
            _next = [[next pageForIndex:endIndex.integerValue] retain];
        }
        else {
            _next = nil;
        }
        _nextOffset = [_next indexAfterDate:_end].integerValue;
        _count = _localObjects.count + next.count - _nextOffset;
    }
    return self;
}

- (id)initWithCoder:(NSCoder *)decoder {
    self = [super init];
    if (self) {
        _localObjects = [[decoder decodeObjectForKey:@"localObjects"] retain];
        _localIndicesByKey = [[decoder decodeObjectForKey:@"localIndicesByKey"] retain];
        _start = [[decoder decodeObjectForKey:@"start"] retain];
        _end = [[decoder decodeObjectForKey:@"end"] retain];
        _next = [[decoder decodeObjectForKey:@"next"] retain];
        _nextOffset = [decoder decodeIntegerForKey:@"nextOffset"];
        _count = [decoder decodeIntegerForKey:@"count"];
    }
    return self;
}

- (void)dealloc
{
    [_localObjects release];
    [_localIndicesByKey release];
    [_start release];
    [_end release];
    [_next release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.localObjects forKey:@"localObjects"];
    [encoder encodeObject:self.localIndicesByKey forKey:@"localIndicesByKey"];
    [encoder encodeObject:self.start forKey:@"start"];
    [encoder encodeObject:self.end forKey:@"end"];
    [encoder encodeObject:self.next forKey:@"next"];
    [encoder encodeInteger:self.nextOffset forKey:@"nextOffset"];
    [encoder encodeInteger:self.count forKey:@"count"];
}

- (NSInteger)localCount {
    return self.localObjects.count;
}

- (id<STDatum>)objectAtIndex:(NSInteger)index {
    NSAssert1(index >= 0, @"Index must be non-negative, was %d", index);
    if (index < self.count) {
        return [self.localObjects objectAtIndex:index];
    }
    else {
        return [self.next objectAtIndex:index + self.nextOffset - self.count];
    }
}

- (NSNumber*)adjustedNextIndex:(NSNumber*)index {
    if (index) {
        NSInteger value = index.integerValue - self.nextOffset;
        if (value < 0) {
            index = nil;
        }
        else {
            index = [NSNumber numberWithInteger:value + self.count];
        }
    }
    return index;
}

- (NSNumber*)indexForKey:(NSString*)key {
    NSNumber* index = [self.localIndicesByKey objectForKey:key];
    if (index) {
        return index;
    }
    else {
        index = [self.next indexForKey:key];
        return [self adjustedNextIndex:index];
    }
}

- (STCachePage*)pageForIndex:(NSInteger)index; {
    if (index < self.count) {
        return self;
    }
    else {
        return [self.next pageForIndex:index + self.nextOffset - self.count];
    }
}

- (NSNumber*)indexAfterDate:(NSDate*)date {
    NSNumber* index = nil;
    for (NSInteger i = self.localCount - 1; i >= 0; i--) {
        id<STDatum> datum = [self objectAtIndex:i];
        if ([datum.timestamp compare:date] == NSOrderedAscending) {
            if (index == nil) {
                index = [self.next indexAfterDate:date];
                index = [self adjustedNextIndex:index];
            }
            break;
        }
        else {
            index = [NSNumber numberWithInteger:i];
        }
    }
    return index;
}

/*
 - (NSArray<STDatum>*)localObjectsAfterDate:(NSDate*)date {
 //TODO
 }
 */

@end
