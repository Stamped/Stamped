//
//  STPageControl.h
//  Stamped
//
//  Created by Landon Judkins on 3/6/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

/*
 Custom PageControl-like control which lets the user specify various attributes of the control.
 
 This element does not page manipulation, just page observation.
 
 2012-08-10
 -Landon
 */

#import <UIKit/UIKit.h>

@interface STPageControl : UIControl

@property (nonatomic, assign) NSInteger currentPage;
@property (nonatomic, assign) BOOL hidesForSinglePage;
@property (nonatomic, assign) NSInteger numberOfPages;
@property (nonatomic, assign) CGFloat spacing;
@property (nonatomic, assign) CGFloat radius;
@property (nonatomic, retain) UIColor* selectedColor;
@property (nonatomic, retain) UIColor* defaultColor;

- (CGSize)sizeForNumberOfPages:(NSInteger)pageCount;
@end
