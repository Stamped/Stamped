//
//  STDatum.h
//  Stamped
//
//  Created by Landon Judkins on 5/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@protocol STDatum <NSObject>

@required
@property (nonatomic, readonly, retain) NSString* key;
@property (nonatomic, readonly, retain) NSDate* timestamp;

@optional
@property (nonatomic, readonly, retain) NSArray* previousTimestamps;
@property (nonatomic, readonly, assign) BOOL repeatable;

@end
