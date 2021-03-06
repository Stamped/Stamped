//
//  CreditPickerViewController.h
//  Stamped
//
//  Created by Devin Doty on 6/12/12.
//
//

#import <UIKit/UIKit.h>
#import "STRestViewController.h"

@protocol CreditPickerViewControllerDelegate;
@interface CreditPickerViewController : STRestViewController

- (id)initWithEntityIdentifier:(NSString*)identifier selectedUsers:(NSArray*)user;

@property(nonatomic,assign) id <CreditPickerViewControllerDelegate> delegate;

@end
@protocol CreditPickerViewControllerDelegate
- (void)creditPickerViewController:(CreditPickerViewController*)controller doneWithUsers:(NSArray*)users;
- (void)creditPickerViewControllerCancelled:(CreditPickerViewController*)controller;
@end