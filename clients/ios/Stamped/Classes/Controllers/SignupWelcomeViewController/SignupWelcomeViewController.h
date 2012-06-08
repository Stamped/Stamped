//
//  SignupWelcomeViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    SignupWelcomeTypeEmail = 0,
    SignupWelcomeTypeTwitter,
    SignupWelcomeTypeFacebook,
} SignupWelcomeType;

@interface SignupWelcomeViewController : UITableViewController {
    UIView *_loadingView;
}

- (id)initWithType:(SignupWelcomeType)type;

@property(nonatomic,retain) NSDictionary *userInfo;
@property(nonatomic,readonly) SignupWelcomeType signupType;
@end
