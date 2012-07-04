//
//  STCachePage.m
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STCachePage.h"
#import "STCache.h"

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
@synthesize created = _created;
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
              created:(NSDate*)created
              andNext:(STCachePage*)next {
    self = [super init];
    if (self) {
        //TODO ensure sorted, with order preservation
        NSAssert1(objects != nil, @"Objects must not be nil for %@", self);
        if (!created) {
            created = [NSDate date];
        }
        _created = [created retain];
        NSAssert1(start != nil, @"Start date must not be nil for %@", self);
        _start = [start retain];
        NSDate* removalDate = nil;
        if (next && next.created.timeIntervalSince1970 > _created.timeIntervalSince1970) {
            removalDate = next.start;
            NSAssert2(_start.timeIntervalSince1970 > removalDate.timeIntervalSince1970,
                      @"Attempted to assign a newer next with a start date before or equal to given start date: %@, %@",
                      start,
                      removalDate);
            NSAssert1(end != nil, @"End must be nil if created after next, was %@", end);
            NSMutableArray* trimmed_objects = [NSMutableArray array];
            for (id<STDatum> datum in objects) {
                if (datum.timestamp.timeIntervalSince1970 > removalDate.timeIntervalSince1970) {
                    [trimmed_objects addObject:datum];
                }
            }
            objects = (NSArray<STDatum>*)trimmed_objects;
        }
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
        if (!end) {
            if (!replacementEnd) {
                replacementEnd = _start;
            }
            end = replacementEnd;
        }
        _end = [end retain];
        NSAssert1(_end, @"End should not be nil for %@", self);
        NSNumber* endIndex = [next indexAfterDate:_end];
        if (endIndex) {
            _next = [[next pageForIndex:endIndex.integerValue] retain];
        }
        else {
            _next = nil;
        }
        _nextOffset = [_next indexAfterDate:_end].integerValue;
        _count = _localObjects.count + _next.count - _nextOffset;
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
        _created = [[decoder decodeObjectForKey:@"created"] retain];
    }
    return self;
}

- (void)dealloc
{
    [_localObjects release];
    [_localIndicesByKey release];
    [_start release];
    [_end release];
    [_created release];
    [_next release];
    [super dealloc];
}

- (void)encodeWithCoder:(NSCoder *)encoder {
    [encoder encodeObject:self.localObjects forKey:@"localObjects"];
    [encoder encodeObject:self.localIndicesByKey forKey:@"localIndicesByKey"];
    [encoder encodeObject:self.start forKey:@"start"];
    [encoder encodeObject:self.end forKey:@"end"];
    [encoder encodeObject:self.created forKey:@"created"];
    [encoder encodeObject:self.next forKey:@"next"];
    [encoder encodeInteger:self.nextOffset forKey:@"nextOffset"];
    [encoder encodeInteger:self.count forKey:@"count"];
}

- (NSInteger)localCount {
    return self.localObjects.count;
}

- (id<STDatum>)objectAtIndex:(NSInteger)index {
    NSAssert1(index >= 0, @"Index must be non-negative, was %d", index);
    if (index < self.localCount) {
        return [self.localObjects objectAtIndex:index];
    }
    else {
        NSAssert1(self.next, @"Next must not be nil for index %d", index);
        return [self.next objectAtIndex:index + self.nextOffset - self.localCount];
    }
}

- (NSNumber*)adjustedNextIndex:(NSNumber*)index {
    if (index) {
        NSInteger value = index.integerValue - self.nextOffset;
        if (value < 0) {
            index = nil;
        }
        else {
            index = [NSNumber numberWithInteger:value + self.localCount];
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
    if (index < self.localCount) {
        return self;
    }
    else {
        return [self.next pageForIndex:index + self.nextOffset - self.localCount];
    }
}

/*
 Nil if and only if count == 0 or beyond end
 */
- (NSNumber*)indexAfterDate:(NSDate*)date {
    NSNumber* index = nil;
    for (NSInteger i = self.localCount - 1; i >= 0; i--) {
        id<STDatum> datum = [self objectAtIndex:i];
        if (datum.timestamp.timeIntervalSince1970 >= date.timeIntervalSince1970) {
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

- (STCachePage*)pageWithAddedPage:(STCachePage*)page {
    if (page.count == 0) {
        return self;
    }
    if (self.created.timeIntervalSince1970 > page.created.timeIntervalSince1970) {
        //NSLog(@"Tried to add a page older than current page,%@,%@",page.created, self.created);
        return self;
    }
    if (self.count == 0) {
        return page;
    }
    if (self.start.timeIntervalSince1970 > page.start.timeIntervalSince1970) {
        //self starts before page
        STCachePage* next;
        if (self.next) {
            next = [self.next pageWithAddedPage:page];
        }
        else {
            next = page;
        }
        if (next == self.next) {
            return self;
        }
        else {
            return [[[STCachePage alloc] initWithObjects:self.localObjects start:self.start end:self.end created:self.created andNext:next] autorelease];
        }
    }
    else {
        //Create new page pointing to this as next
        STCachePage* finalResult = [[[STCachePage alloc] initWithObjects:page.localObjects start:page.start end:page.end created:page.created andNext:self] autorelease];
        NSAssert2(finalResult.count >= page.count, @"Count should have been at least %d was %d", page.count, finalResult.count);
        return finalResult;
    }
}


- (STCachePage*)pageWithUpdatesFromAccelerator:(id<STCacheAccelerator>)accelerator {
    BOOL different = NO;
    STCachePage* next = [self.next pageWithUpdatesFromAccelerator:accelerator];
    if (next != self.next) {
        different = YES;
    }
    NSMutableArray<STDatum>* localObjects = (id)[NSMutableArray array];
    if (self.localObjects.count) {
        for (id<STDatum> datum in self.localObjects) {
            id<STDatum> replacement = [accelerator datumForCurrentDatum:datum];
            if (replacement && [[replacement timestamp] isEqualToDate:[datum timestamp]]) {
                [localObjects addObject:replacement];
                different = YES;
            }
            else {
                [localObjects addObject:datum];
            }
        }
    }
    if (different) {
        return [[[STCachePage alloc] initWithObjects:localObjects start:self.start end:self.end created:self.created andNext:next] autorelease];
    }
    else {
        return self;
    }
}

/*
 - (NSArray<STDatum>*)localObjectsAfterDate:(NSDate*)date {
 //TODO
 }
 */

@end
