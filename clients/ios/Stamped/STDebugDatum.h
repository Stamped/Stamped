//
//  STDebugDatum.h
//  Stamped
//
//  Created by Landon Judkins on 4/20/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@interface STDebugDatum : NSObject

- (id)initWithObject:(id)object;

@property (nonatomic, readonly, retain) id object;
@property (nonatomic, readonly, retain) NSDate* created;

@end
