//
//  FindFriendsViewController.h
//  Stamped
//
//  Created by Robert Sesek on 9/10/11.
//  Copyright 2011 Stamped. All rights reserved.
//

#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

typedef enum {
  FindFriendsSourceInvalid = 0,
  FindFriendsFromContacts = 1,
  FindFriendsFromTwitter = 2
} FindFriendsSource;

@interface FindFriendsViewController : UIViewController<RKObjectLoaderDelegate,
                                                        RKRequestDelegate>

@property (nonatomic, retain) IBOutlet UIButton* contactsButton;
@property (nonatomic, retain) IBOutlet UIButton* twitterButton;
@property (nonatomic, retain) IBOutlet UIImageView* nipple;

- (id)initWithFindSource:(FindFriendsSource)source;

- (IBAction)done:(id)sender;

- (IBAction)findFromContacts:(id)sender;
- (IBAction)findFromTwitter:(id)sender;

@end
