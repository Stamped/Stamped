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

@interface STMenuController ()
- (void)showWelcome;
@end

@implementation STMenuController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!LOGGED_IN) {
        [self showWelcome];
    }
    
}


#pragma mark - Welcome

- (void)showWelcome {
    
    STWelcomeViewController *welcomeController = [[STWelcomeViewController alloc] init];
    welcomeController.delegate = (id<STWelcomeViewControllerDelegate>)self;
    [self.view addSubview:welcomeController.view];
    welcomeController.view.frame = self.view.bounds;
    [welcomeController animateIn];
    
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
        [self presentModalViewController:controller animated:YES];
        [controller release];
    
    } else if (option == STWelcomeViewControllerOptionTwitter) {
        
        if (NO && NSClassFromString(@"TWTweetComposeViewController")) {
            
            TwitterAccountsViewController *controller = [[TwitterAccountsViewController alloc] init];
            controller.delegate = (id<TwitterAccountsViewControllerDelegate>)self;
            STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
            [self presentModalViewController:navController animated:YES];
            [controller release];
            [navController release];
            
        } else {
            
            STSocialAuthViewController *controller = [[STSocialAuthViewController alloc] initWithAuthType:SocialAuthTypeTwitter];
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


@end
