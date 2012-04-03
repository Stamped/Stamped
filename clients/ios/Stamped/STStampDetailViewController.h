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

#import "STStandardViewController.h"
#import "STContainerViewController.h"

@class Stamp;

@interface STStampDetailViewController : STContainerViewController

- (id)initWithStamp:(Stamp*)stamp;

@end
