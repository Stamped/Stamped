//
//  STGenericCollectionSlice.h
//  Stamped
//
//  Created by Landon Judkins on 4/3/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericSlice.h"

@interface STGenericCollectionSlice : STGenericSlice

@property (nonatomic, readwrite, copy) NSString* query;
@property (nonatomic, readwrite, copy) NSString* category;
@property (nonatomic, readwrite, copy) NSString* subcategory;
@property (nonatomic, readwrite, copy) NSString* viewport;
@property (nonatomic, readwrite, copy) NSNumber* quality;
@property (nonatomic, readwrite, copy) NSNumber* deleted;
@property (nonatomic, readwrite, copy) NSNumber* comments;
@property (nonatomic, readwrite, copy) NSNumber* unique;

@end
