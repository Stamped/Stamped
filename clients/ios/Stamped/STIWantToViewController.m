//
//  STIWantToViewController.m
//  Stamped
//
//  Created by Landon Judkins on 4/28/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STIWantToViewController.h"
#import "Util.h"
#import "UIColor+Stamped.h"
#import "UIFont+Stamped.h"
#import <QuartzCore/QuartzCore.h>
#import "STConsumptionViewController.h"
#import "STButton.h"
#import "STConfiguration.h"
#import "STConsumptionMapViewController.h"
#import "STMenuController.h"
#import "STAppDelegate.h"
#import "STNavigationItem.h"

@interface STIWantToViewController ()

@end

@implementation STIWantToViewController

- (id)init {
    self = [super init];
    if (self) {
    }
    return self;
}

- (void)login:(id)sender {
    
    STMenuController *controller = ((STAppDelegate*)[[UIApplication sharedApplication] delegate]).menuController;
    [controller showSignIn];
    
}

- (void)viewDidLoad {
    [super viewDidLoad];
    
    if (!LOGGED_IN) {
        
        STNavigationItem *button = [[STNavigationItem alloc] initWithTitle:@"Sign in" style:UIBarButtonItemStyleBordered target:self action:@selector(login:)];
        self.navigationItem.rightBarButtonItem = button;
        [button release];
        
    } else {
        
        [Util addCreateStampButtonToController:self];
        
    }
    
    self.view.backgroundColor = [UIColor colorWithRed:0.949f green:0.949f blue:0.949f alpha:1.0f];
    
    CGFloat cellWidth = (self.scrollView.frame.size.width-10.0f)/2;
    NSArray *categories = [Util categories];
    UIImage *image = [UIImage imageNamed:@"want_btn_bg.png"];
    UIImage *imageHi = [UIImage imageNamed:@"want_btn_bg_hi.png"];
    CGRect buttonFrame = CGRectMake(5, 8, cellWidth, image.size.height);
    
    for (NSInteger i = 0; i < categories.count; i++) {
        
        NSString *category = [categories objectAtIndex:i];
        NSString *imageName = [NSString stringWithFormat:@"consumption_%@", category];
        
        UIButton *button = [UIButton buttonWithType:UIButtonTypeCustom];
        button.adjustsImageWhenHighlighted = NO;
        button.frame = buttonFrame;
        [button setBackgroundImage:[image stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateNormal];
        [button setBackgroundImage:[imageHi stretchableImageWithLeftCapWidth:(image.size.width/2) topCapHeight:0] forState:UIControlStateHighlighted];
        [button setImage:[UIImage imageNamed:imageName] forState:UIControlStateNormal];
        [button addTarget:self action:@selector(buttonHit:) forControlEvents:UIControlEventTouchUpInside];
        [self.scrollView addSubview:button];
        button.tag = i;
        
        if (i % 2 != 0) {
            buttonFrame.origin.y += (image.size.height+4.0f);
            buttonFrame.origin.x = 4.0f;
        } else {
            buttonFrame.origin.x += (cellWidth+2.0f);
        }
        
    }
    
}

- (void)viewDidUnload {
    [super viewDidUnload];
}


#pragma mark - Actions

- (void)buttonHit:(UIButton*)sender {
    
    NSString *category = [[Util categories] objectAtIndex:sender.tag];
    UIViewController *controller = nil;
    
    NSDictionary* categoryMapping = [NSDictionary dictionaryWithObjectsAndKeys:
                                     @"food", @"food",
                                     @"book", @"book",
                                     @"music", @"music",
                                     @"film", @"film",
                                     @"app", @"download",
                                     @"app", @"other",
                                     nil];
    category = [categoryMapping objectForKey:category];
    if (category) {
        if ([category isEqualToString:@"food"]) {
            controller = [[[STConsumptionMapViewController alloc] init] autorelease];
        }
        else {
            controller = [[[STConsumptionViewController alloc] initWithCategory:category] autorelease];
        }
    }
    
    if (controller) {
        [Util pushController:controller modal:NO animated:YES];
        //[self.navigationController pushViewController:controller animated:YES];
    } else {
        [Util warnWithMessage:[NSString stringWithFormat:@"controller for %@ not implemented yet...", category] andBlock:nil];
    }
    
}

+ (void)setupConfigurations {
    [STConsumptionMapViewController setupConfigurations];
    [STConsumptionViewController setupConfigurations];
}

@end
