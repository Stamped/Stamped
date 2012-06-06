//
//  STButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/18/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STButton : UIView

- (id)initWithFrame:(CGRect)frame 
         normalView:(UIView*)normalView 
         activeView:(UIView*)activeView 
             target:(id)target 
          andAction:(SEL)selector;

+ (STButton*)buttonWithNormalImage:(UIImage*)normalImage
                       activeImage:(UIImage*)activeImage 
                            target:(id)target 
                         andAction:(SEL)selector;

@property (nonatomic, readwrite, assign) BOOL enabled;
@property (nonatomic, readwrite, retain) id message;
@property (nonatomic, readwrite, assign) id target;
@property (nonatomic, readwrite, assign) SEL action;

@end
