//
//  STCreditPickerController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/21/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <Foundation/Foundation.h>

@class STCreditTextField;

@protocol STCreditPickerControllerDelegate
- (void)creditTextFieldDidBeginEditing:(STCreditTextField*)textField;
- (void)creditTextFieldDidEndEditing:(STCreditTextField*)textField;
- (BOOL)creditTextFieldShouldReturn:(STCreditTextField*)textField;
@end

@interface STCreditPickerController : NSObject <UITextFieldDelegate,
                                                UITableViewDelegate,
                                                UITableViewDataSource>

// All of these are WEAK references.
@property (nonatomic, assign) STCreditTextField* creditTextField;
@property (nonatomic, assign) id<STCreditPickerControllerDelegate> delegate;

@end
