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

@property (nonatomic, readwrite, assign) BOOL enabled;

@end