//
//  STEntityDetailComponentFactory.h
//  Stamped
//
//  Created by Landon Judkins on 3/23/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>
#import "STViewDelegate.h"
#import "STEntityDetail.h"

@protocol STEntityDetailComponentFactory <NSObject>

- (NSOperation*)createViewWithEntityDetail:(id<STEntityDetail>)anEntityDetail andCallbackBlock:(STViewCreatorCallback)aBlock;

@end
