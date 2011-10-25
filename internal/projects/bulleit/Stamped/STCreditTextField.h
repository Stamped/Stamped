//
//  STCreditTextField.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface STCreditTextField : UIView <UITextFieldDelegate>

- (void)becomeFirstResponder;
- (void)resignFirstResponder;

@property (nonatomic, assign) id<UITextFieldDelegate> delegate;
@property (nonatomic, copy) NSString* text;

@end
