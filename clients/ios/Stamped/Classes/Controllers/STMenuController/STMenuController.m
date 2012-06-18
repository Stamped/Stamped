//
//  STMenuController.m
//  Stamped
//
//  Created by Devin Doty on 5/30/12.
//
//

#import "STMenuController.h"
#import "EntityViewController.h"
#import "STWelcomeViewController.h"
#import "LoginViewController.h"
#import "TwitterAccountsViewController.h"
#import "STSocialAuthViewController.h"
#import "STRootViewController.h"
#import "SignupViewController.h"
#import "STFacebook.h"
#import "STTwitter.h"

#import "PostStampShareView.h"

@interface STMenuController ()
@property(nonatomic,retain) LoginViewController *loginController;
@end

@implementation STMenuController

@synthesize loginController = _loginController;

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!LOGGED_IN) {
        [self showWelcome:YES];
    }
    
}

- (void)resetNavButtons {} // overide showing nav buttons, already handled by app


#pragma mark - Welcome

- (void)showWelcome:(BOOL)animated {
    
    STWelcomeViewController *welcomeController = [[STWelcomeViewController alloc] init];
    welcomeController.delegate = (id<STWelcomeViewControllerDelegate>)self;
    [self.view addSubview:welcomeController.view];
    welcomeController.view.frame = self.view.bounds;
    if (animated) {
        [welcomeController animateIn];
    } else {
        [welcomeController popIn];
    }
    
}

- (void)showSignIn {
    
    STWelcomeViewController *welcomeController = [[STWelcomeViewController alloc] init];
    welcomeController.delegate = (id<STWelcomeViewControllerDelegate>)self;
    [self.view addSubview:welcomeController.view];
    welcomeController.view.frame = self.view.bounds;
    [welcomeController showSignIn];
    [welcomeController popIn];
    
    
}


#pragma mark - STWelcomeViewControllerDelegate

- (void)stWelcomeViewControllerDismiss:(STWelcomeViewController*)controller {
    
    [controller.view removeFromSuperview];
    [controller release];
    
}

- (void)stWelcomeViewController:(STWelcomeViewController*)controller selectedOption:(STWelcomeViewControllerOption)option {
    
    [controller.view removeFromSuperview];
    [controller release];
    
    if (option == STWelcomeViewControllerOptionLogin) {
    
        LoginViewController *controller = [[LoginViewController alloc] init];
        controller.delegate = (id<LoginViewControllerDelegate>)self;
        [self.view addSubview:controller.view];
        controller.view.frame = self.view.bounds;
        self.loginController = controller;
        [controller release];
        
        [self.loginController animateIn];
    
    } else if (option == STWelcomeViewControllerOptionTwitter) {
        
        if (NSClassFromString(@"TWTweetComposeViewController") && [TWTweetComposeViewController canSendTweet]) {
            
            TwitterAccountsViewController *controller = [[TwitterAccountsViewController alloc] init];
            controller.delegate = (id<TwitterAccountsViewControllerDelegate>)self;
            STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
            [self presentModalViewController:navController animated:YES];
            [controller release];
            [navController release];
            
        } else {
            
            STSocialAuthViewController *controller = [[STSocialAuthViewController alloc] initWithAuthType:SocialAuthTypeTwitter];
            controller.delegate = (id<SocialAuthViewControllerDelegate>)self;
            STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
            [self presentModalViewController:navController animated:YES];
            [controller release];
            [navController release];
            
        }
    
    } else if (option == STWelcomeViewControllerOptionSignup) {
        
        SignupViewController *controller = [[SignupViewController alloc] init];
        controller.delegate = (id<SignupViewControllerDelegate>)self;
        STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
        [self presentModalViewController:navController animated:YES];
        [controller release];
        [navController release];
        
    } else if (option == STWelcomeViewControllerOptionFacebook) {
        
        STSocialAuthViewController *controller = [[STSocialAuthViewController alloc] initWithAuthType:SocialAuthTypeFacebook];
        controller.delegate = (id<SocialAuthViewControllerDelegate>)self;
        STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
        [self presentModalViewController:navController animated:YES];
        [controller release];
        [navController release];
    }
 
    
}


#pragma mark - SignupViewControllerDelegate

- (void)signupViewControllerCancelled:(SignupViewController*)controller {
    [self dismissModalViewControllerAnimated:YES];
}


#pragma mark - TwitterAccountsViewControllerDelegate

- (void)twitterAccountsViewControllerCancelled:(TwitterAccountsViewController*)controller {
    
    [self dismissModalViewControllerAnimated:YES];
    
}

- (void)twitterAccountsViewControllerSuccessful:(TwitterAccountsViewController*)controller {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


#pragma mark - LoginViewControllerDelegate

- (void)loginViewControllerDidDismiss:(LoginViewController*)controller {
    [controller.view removeFromSuperview];
    self.loginController = nil;
}


#pragma mark - SocialAuthViewControllerDelegate

- (void)socialAuthViewControllerFinished:(STSocialAuthViewController*)controller {
    
    [self dismissModalViewControllerAnimated:YES];
    
}

- (void)socialAuthViewControllerFailed:(STSocialAuthViewController*)controller {
    
    [self dismissModalViewControllerAnimated:YES];

    dispatch_after(dispatch_time(DISPATCH_TIME_NOW, 0.4f * NSEC_PER_SEC), dispatch_get_main_queue(), ^(void){
        [self showWelcome:NO];
    });
    
}


@end
