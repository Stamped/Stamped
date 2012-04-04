//
//  STContainerViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STStandardViewController.h"
#import "STViewDelegate.h"
#import "STViewContainer.h"

@interface STContainerViewController : UIViewController <STViewDelegate, UIScrollViewDelegate>

@property (nonatomic, readonly, retain) STScrollViewContainer* scrollView;

- (void)shouldFinishLoading;

- (void)userPulledToReload;

- (void)reloadData;

@end
