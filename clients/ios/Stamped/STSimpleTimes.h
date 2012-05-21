//
//  STSimpleTimes.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import <RestKit/RestKit.h>
#import "STTimes.h"

@interface STSimpleTimes : NSObject <STTimes, NSCoding>

@property (nonatomic, readwrite, retain) NSArray<STHours>* sun;
@property (nonatomic, readwrite, retain) NSArray<STHours>* mon;
@property (nonatomic, readwrite, retain) NSArray<STHours>* tue;
@property (nonatomic, readwrite, retain) NSArray<STHours>* wed;
@property (nonatomic, readwrite, retain) NSArray<STHours>* thu;
@property (nonatomic, readwrite, retain) NSArray<STHours>* fri;
@property (nonatomic, readwrite, retain) NSArray<STHours>* sat;

+ (RKObjectMapping*)mapping;

@end
