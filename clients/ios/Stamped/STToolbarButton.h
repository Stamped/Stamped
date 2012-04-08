//
//  STToolbarButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/4/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STToolbarButton : UIView

- (id)initWithNormalOffImage:(UIImage*)normalOffImage offText:(NSString*)offText andOnText:(NSString*)onText;
- (void)setTarget:(id)target withSelector:(SEL)selector;
- (void)defaultHandler:(id)myself;

@property (nonatomic, readwrite, assign) BOOL on;
@property (nonatomic, readwrite, retain) UIImage* normalOnImage;
@property (nonatomic, readwrite, retain) UIImage* touchedOnImage;
@property (nonatomic, readwrite, retain) UIImage* normalOffImage;
@property (nonatomic, readwrite, retain) UIImage* touchedOffImage;

@end
