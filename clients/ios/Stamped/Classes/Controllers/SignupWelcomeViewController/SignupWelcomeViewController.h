//
//  SignupWelcomeViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import <UIKit/UIKit.h>
#import "STAccountParameters.h"

typedef enum {
    SignupWelcomeTypeEmail = 0,
    SignupWelcomeTypeTwitter,
    SignupWelcomeTypeFacebook,
} SignupWelcomeType;

@interface SignupWelcomeViewController : UITableViewController {
    UIView *_loadingView;
}

- (id)initWithType:(SignupWelcomeType)type;

@property(nonatomic,retain) STAccountParameters *userInfo;

@end
