//
//  STConfirmationView.h
//  Stamped
//
//  Created by Landon Judkins on 3/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STConfirmationView : UIView

- (id)initWithTille:(NSString*)title subtitle:(NSString*)subtitle andIconImage:(UIImage*)image;

+ (void)displayConfirmationWithTitle:(NSString*)title subtitle:(NSString*)subtitle andIconImage:(UIImage*)image;

@property (nonatomic, readwrite, retain) UIImage* image;

@end
