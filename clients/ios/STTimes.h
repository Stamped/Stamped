//
//  STTimes.h
//  Stamped
//
//  Created by Landon Judkins on 3/29/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STHours.h"

@protocol STTimes <NSObject>

@property (nonatomic, readonly, retain) NSArray<STHours>* sun;
@property (nonatomic, readonly, retain) NSArray<STHours>* mon;
@property (nonatomic, readonly, retain) NSArray<STHours>* tue;
@property (nonatomic, readonly, retain) NSArray<STHours>* wed;
@property (nonatomic, readonly, retain) NSArray<STHours>* thu;
@property (nonatomic, readonly, retain) NSArray<STHours>* fri;
@property (nonatomic, readonly, retain) NSArray<STHours>* sat;

@end
