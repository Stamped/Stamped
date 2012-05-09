//
//  STConsumptionSlice.h
//  Stamped
//
//  Created by Landon Judkins on 5/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericCollectionSlice.h"

@interface STConsumptionSlice : STGenericCollectionSlice

@property (nonatomic, readwrite, copy) NSString* scope;
@property (nonatomic, readwrite, copy) NSString* filter;

@end
