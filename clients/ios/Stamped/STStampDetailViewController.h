//
//  STStampDetailViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 3/26/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import <MessageUI/MFMailComposeViewController.h>
#import <RestKit/RestKit.h>
#import <UIKit/UIKit.h>

#import "STViewController.h"

@class Stamp;
@class STStampDetailCardView;
@class STStampDetailHeader;
@class STStampDetailToolbar;

@interface STStampDetailViewController : STViewController<UIActionSheetDelegate,
                                                          MFMailComposeViewControllerDelegate>

- (id)initWithStamp:(Stamp*)stamp;

@property (nonatomic, retain) IBOutlet UIScrollView* scrollView;
@property (nonatomic, retain) IBOutlet STStampDetailCardView* cardView;
@property (nonatomic, retain) IBOutlet STStampDetailToolbar* toolbar;
@property (nonatomic, retain) IBOutlet STStampDetailHeader* header;

@end
