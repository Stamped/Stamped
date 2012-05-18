//
//  STPreviewsView.h
//  Stamped
//
//  Created by Landon Judkins on 4/25/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>
#import "STStamp.h"
#import "STCancellation.h"

@interface STPreviewsView : UIView

- (void)setupWithStamp:(id<STStamp>)stamp maxRows:(NSInteger)maxRows;
- (void)setupWithPreview:(id<STPreviews>)previews maxRows:(NSInteger)maxRows;

+ (CGFloat)previewHeightForStamp:(id<STStamp>)stamp andMaxRows:(NSInteger)maxRows;
+ (CGFloat)previewHeightForPreviews:(id<STPreviews>)previews andMaxRows:(NSInteger)maxRows;

+ (NSArray*)imagesForPreviewWithStamp:(id<STStamp>)stamp andMaxRows:(NSInteger)maxRows;
+ (NSArray*)imagesForPreviewWithPreviews:(id<STPreviews>)previews andMaxRows:(NSInteger)maxRows;

@end
