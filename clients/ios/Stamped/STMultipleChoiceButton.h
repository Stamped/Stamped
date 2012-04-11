//
//  STMultipleChoiceButton.h
//  Stamped
//
//  Created by Landon Judkins on 4/9/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STMultipleChoiceButton : UIButton

- (id)initWithTitle:(NSString*)title message:(NSString*)message choices:(NSArray*)choices andFrame:(CGRect)frame;

- (void)setTarget:(id)target withSelector:(SEL)selector;

@property (nonatomic, readonly, copy) NSString* selectedChoice;

@end
