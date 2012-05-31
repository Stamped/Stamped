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

@interface SignupWelcomeViewController : UITableViewController

- (id)initWithType:(SignupWelcomeType)type;

@property(nonatomic,readonly) SignupWelcomeType signupType;
@end
