//
//  STUserCollectionSlice.h
//  Stamped
//
//  Created by Landon Judkins on 4/11/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCollectionSlice.h"

@interface STFriendsSlice : STGenericCollectionSlice

@property (nonatomic, readwrite, copy) NSNumber* distance;
@property (nonatomic, readwrite, copy) NSNumber* inclusive;

@end
