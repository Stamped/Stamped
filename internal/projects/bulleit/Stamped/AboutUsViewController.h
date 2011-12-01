//
//  AboutUsViewController.h
//  Stamped
//
//  Created by Jake Zien on 11/2/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface AboutUsViewController : UIViewController

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet UIView* contentView;
@property (nonatomic, retain) IBOutlet UILabel* versionLabel;

- (IBAction)settingsButtonPressed:(id)sender;
- (IBAction)followButtonPressed:(id)sender;
- (IBAction)stampedButtonPressed:(id)sender;

@end