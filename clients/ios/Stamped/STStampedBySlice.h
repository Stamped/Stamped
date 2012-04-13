//
//  STStampedBySlice.h
//  Stamped
//
//  Created by Landon Judkins on 4/13/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCollectionSlice.h"

@interface STStampedBySlice : STGenericCollectionSlice

@property (nonatomic, readwrite, copy) NSString* entityID;
@property (nonatomic, readwrite, copy) NSString* group;

@end
