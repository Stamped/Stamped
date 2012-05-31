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
#import "STRootViewController.h"

@interface STMenuController ()
- (void)showWelcome;
@end

@implementation STMenuController

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!LOGGED_IN || YES) {
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
        
        TwitterAccountsViewController *controller = [[TwitterAccountsViewController alloc] init];
        controller.delegate = (id<TwitterAccountsViewControllerDelegate>)self;
        STRootViewController *navController = [[STRootViewController alloc] initWithRootViewController:controller];
        [self presentModalViewController:navController animated:YES];
        [controller release];
        [navController release];
         
        
    }
 
    
}


#pragma mark - TwitterAccountsViewControllerDelegate

- (void)twitterAccountsViewControllerCancelled:(TwitterAccountsViewController*)controller {
    
    [self dismissModalViewControllerAnimated:YES];
    
}


@end
