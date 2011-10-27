//
//  FindFriendsViewController.h
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "FBConnect.h"

@class STSearchField;

typedef enum {
  FindFriendsSourceInvalid = 0,
  FindFriendsFromContacts = 1,
  FindFriendsFromTwitter = 2,
  FindFriendsFromStamped = 3,
  FindFriendsFromFacebook = 4
} FindFriendsSource;

@interface FindFriendsViewController : UIViewController<RKObjectLoaderDelegate,
                                                        RKRequestDelegate,
                                                        FBRequestDelegate,
                                                        FBSessionDelegate,
                                                        UITableViewDelegate,
                                                        UITableViewDataSource,
                                                        UITextFieldDelegate,
                                                        UIWebViewDelegate>

@property (nonatomic, retain) IBOutlet UIButton* contactsButton;
@property (nonatomic, retain) IBOutlet UIButton* twitterButton;
@property (nonatomic, retain) IBOutlet UIButton* stampedButton;
@property (nonatomic, retain) IBOutlet UIButton* facebookButton;
@property (nonatomic, retain) IBOutlet UIImageView* nipple;
@property (nonatomic, retain) IBOutlet UITableView* tableView;
@property (nonatomic, retain) IBOutlet STSearchField* searchField;
@property (nonatomic, retain) NSMutableArray* followedUsers;
@property (nonatomic, retain) IBOutlet UIView* signInTwitterView;
@property (nonatomic, retain) IBOutlet UIView* signInFacebookView;
@property (nonatomic, retain) IBOutlet UIView* signInAuthView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* signInTwitterActivityIndicator;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* signInFacebookActivityIndicator;
@property (nonatomic, retain) IBOutlet UIButton* signInTwitterConnectButton;
@property (nonatomic, retain) IBOutlet UIButton* signInFacebookConnectButton;

- (id)initWithFindSource:(FindFriendsSource)source;

- (IBAction)done:(id)sender;

- (IBAction)findFromContacts:(id)sender;
- (IBAction)findFromTwitter:(id)sender;
- (IBAction)findFromStamped:(id)sender;
- (IBAction)findFromFacebook:(id)sender;
- (IBAction)connectToTwitterButtonPressed:(id)sender;
- (IBAction)connectToFacebookButtonPressed:(id)sender;

@end
