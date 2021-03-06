//
//  STGenericSlice.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STStampedParameter.h"

@interface STGenericSlice : STStampedParameter

@property (nonatomic, readwrite, copy) NSNumber* limit;
@property (nonatomic, readwrite, copy) NSNumber* offset;
@property (nonatomic, readwrite, copy) NSString* sort;
@property (nonatomic, readwrite, copy) NSNumber* reverse;
@property (nonatomic, readwrite, copy) NSString* coordinates;
@property (nonatomic, readwrite, copy) NSDate* since;
@property (nonatomic, readwrite, copy) NSDate* before;

- (id)resizedSliceWithLimit:(NSNumber*)limit andOffset:(NSNumber*)offset;

@property (nonatomic, readonly, assign) NSInteger end;

@end
