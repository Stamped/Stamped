//
//  STCachePage.h
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STDatum.h"

@protocol STCacheAccelerator;

@interface STCachePage : NSObject <NSCoding>

@property (nonatomic, readonly, retain) NSDate* start;
@property (nonatomic, readonly, retain) NSDate* end;
@property (nonatomic, readonly, retain) NSDate* created;
@property (nonatomic, readonly, retain) STCachePage* next;

//Convenience methods
@property (nonatomic, readonly, assign) NSInteger localCount;
@property (nonatomic, readonly, assign) NSInteger count;

- (id)initWithObjects:(NSArray<STDatum>*)objects 
                start:(NSDate*)start
                  end:(NSDate*)end 
              created:(NSDate*)created
              andNext:(STCachePage*)next;

- (id<STDatum>)objectAtIndex:(NSInteger)index;
- (NSNumber*)indexForKey:(NSString*)key;
- (STCachePage*)pageForIndex:(NSInteger)index;
- (NSNumber*)indexAfterDate:(NSDate*)date;
- (STCachePage*)pageWithAddedPage:(STCachePage*)page;
- (STCachePage*)pageWithUpdatesFromAccelerator:(id<STCacheAccelerator>)accelerator;
- (STCachePage*)pageWithoutDatumsForKeys:(NSSet*)doomedIDs;
- (STCachePage*)pageWithDatums:(NSArray<STDatum>*)datums;

@end
