//
//  STCreditTextField.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@class STCreditTextField;

@protocol STCreditTextFieldDelegate <UITextFieldDelegate>
- (void)creditTextFieldDidBeginEditing:(STCreditTextField*)textField;
- (void)creditTextFieldDidEndEditing:(STCreditTextField*)textField;
- (BOOL)creditTextFieldShouldReturn:(STCreditTextField*)textField;
@end

@interface STCreditTextField : UITextField <UITextFieldDelegate>
@property (nonatomic, assign) id<STCreditTextFieldDelegate> subDelegate;
@end
