//
//  STStampsView.h
//  Stamped
//
//  Created by Landon Judkins on 4/5/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STGenericCollectionSlice.h"

@interface STStampsView : UITableView

- (id)initWithFrame:(CGRect)frame;

@property (nonatomic, readwrite, copy) STGenericCollectionSlice* slice;

@end
