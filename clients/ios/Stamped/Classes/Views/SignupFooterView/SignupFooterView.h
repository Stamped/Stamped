//
//  SignupFooterView.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>

@protocol SignupFooterViewDelegate;
@interface SignupFooterView : UIView

@property(nonatomic,assign) id <SignupFooterViewDelegate> delegate;

@end

@protocol SignupFooterViewDelegate
- (void)signupFooterViewCreate:(SignupFooterView*)view;
- (void)signupFooterViewTermsOfUse:(SignupFooterView *)view;
- (void)signupFooterViewPrivacy:(SignupFooterView *)view;
@end
