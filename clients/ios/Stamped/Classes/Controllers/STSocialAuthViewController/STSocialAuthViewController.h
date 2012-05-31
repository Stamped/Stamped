//
//  STSocialAuthViewController.h
//  Stamped
//
//  Created by Devin Doty on 5/31/12.
//
//

#import <UIKit/UIKit.h>

typedef enum {
    SocialAuthTypeTwitter = 0,
    SocialAuthTypeFacebook,
} SocialAuthType;

@protocol SocialAuthViewControllerDelegate;
@interface STSocialAuthViewController : UIViewController {
    UIActivityIndicatorView *_activityView;
}

- (id)initWithAuthType:(SocialAuthType)type;

@property(nonatomic,assign) id <SocialAuthViewControllerDelegate> delegate;
@end

@protocol SocialAuthViewControllerDelegate
- (void)socialAuthViewControllerFailed:(STSocialAuthViewController*)controller;
@end