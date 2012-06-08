//
//  SignupFooterView.h
//  Stamped
//
//  Created by Devin Doty on 6/1/12.
//
//

#import <UIKit/UIKit.h>

@protocol SignupFooterViewDelegate;
@interface SignupFooterView : UIView {
    UIActivityIndicatorView *_activityView;
    UIButton *_button;
}

@property(nonatomic,assign) id <SignupFooterViewDelegate> delegate;
@property(nonatomic,assign,getter = isLoading) BOOL loading;

@end

@protocol SignupFooterViewDelegate
- (void)signupFooterViewCreate:(SignupFooterView*)view;
- (void)signupFooterViewTermsOfUse:(SignupFooterView *)view;
- (void)signupFooterViewPrivacy:(SignupFooterView *)view;
@end
