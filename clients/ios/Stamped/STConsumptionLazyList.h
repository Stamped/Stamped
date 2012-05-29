//
//  STConsumptionLazyList.h
//  Stamped
//
//  Created by Landon Judkins on 4/30/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STGenericSliceList.h"
#import "STStampedAPI.h"

@interface STConsumptionLazyList : STGenericLazyList

- (id)initWithScope:(STStampedAPIScope)scope
            section:(NSString*)section 
         subsection:(NSString*)subsection;

@property (nonatomic, readonly, copy) NSString* section;
@property (nonatomic, readonly, copy) NSString* subsection;
@property (nonatomic, readonly, assign) STStampedAPIScope scope;

@end
