//
//  STPreviewsView.h
//  Stamped
//
//  Created by Landon Judkins on 4/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"

@interface STPreviewsView : UIView

- (id)initWithStamp:(id<STStamp>)stamp andMaxRows:(NSInteger)maxRows;

+ (CGFloat)previewHeightForStamp:(id<STStamp>)stamp andMaxRows:(NSInteger)maxRows;

@end