//
//  WelcomeViewController.h
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "StampCustomizerViewController.h"

@class UserImageView;

@interface WelcomeViewController : UIViewController
    <UIScrollViewDelegate, StampCustomizerViewControllerDelegate>

@property (nonatomic, retain) IBOutlet UIView* contentView;
@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;

@property (nonatomic, retain) IBOutlet UINavigationController* findFriendsNavigationController;

@property (nonatomic, retain) IBOutlet UIImageView* userStampImageView;
@property (nonatomic, retain) IBOutlet UserImageView* userImageView;
@property (nonatomic, retain) IBOutlet UIImageView* largeStampColorImageView;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp0;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp1;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp2;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp3;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp4;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp5;
@property (nonatomic, retain) IBOutlet UIButton* galleryStamp6;

@property (nonatomic, retain) IBOutlet UIButton* nextButton;
@property (nonatomic, retain) IBOutlet UIButton* backButton;
@property (nonatomic, retain) IBOutlet UIButton* readyButton;

@property (nonatomic, retain) IBOutlet UILabel* page1Title;
@property (nonatomic, retain) IBOutlet UILabel* page2Title;
@property (nonatomic, retain) IBOutlet UILabel* page3Title;

- (IBAction)backButtonPressed:(id)sender;
- (IBAction)nextButtonPressed:(id)sender;
- (IBAction)findfromContacts:(id)sender;
- (IBAction)findFromTwitter:(id)sender;
- (IBAction)findFromFacebook:(id)sender;
- (IBAction)findFromStamped:(id)sender;
- (IBAction)dismissWelcomeView:(id)sender;
- (IBAction)stampCustomizerButtonPressed:(id)sender;
- (IBAction)stampButtonPressed:(id)sender;

@end
