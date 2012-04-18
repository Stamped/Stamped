//
//  STContainerViewController.h
//  Stamped
//
//  Created by Landon Judkins on 4/2/12.
//  Copyright (c) 2012 Stamped, Inc. All rights reserved.
//

#import "STViewDelegate.h"
#import "STViewContainer.h"
#import "STScrollViewContainer.h"

@interface STContainerViewController : UIViewController <STViewDelegate, UIScrollViewDelegate, UITextFieldDelegate>

@property (nonatomic, readonly, retain) STScrollViewContainer* scrollView;

- (void)shouldFinishLoading;

- (void)userPulledToReload;

- (void)reloadData;

- (void)reloadStampedData;

@property (nonatomic, readonly, retain) UIView* toolbar;

@end
