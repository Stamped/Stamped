//
//  SharingSettingsViewController.h
//  Stamped
//
//  Created by Jake Zien on 10/31/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>
#import <RestKit/RestKit.h>
#import "FBConnect.h"

@interface SharingSettingsViewController : UIViewController <RKRequestDelegate>

@property (nonatomic, retain) IBOutlet UIImageView* twitterIconView;
@property (nonatomic, retain) IBOutlet UIImageView* fbIconView;
@property (nonatomic, retain) IBOutlet UIButton* twitterConnectButton;
@property (nonatomic, retain) IBOutlet UIButton* fbConnectButton;
@property (nonatomic, retain) IBOutlet UILabel* twitterLabel;
@property (nonatomic, retain) IBOutlet UILabel* fbLabel;
@property (nonatomic, retain) IBOutlet UILabel* twitterNameLabel;
@property (nonatomic, retain) IBOutlet UILabel* fbNameLabel;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;

-(IBAction)twitterButtonPressed:(id)sender;
-(IBAction)fbButtonPressed:(id)sender;
-(IBAction)settingsButtonPressed:(id)sender;

@end
