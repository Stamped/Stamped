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
- (void)cancelPendingRequests;

- (UIView*)loadToolbar;

- (void)unloadToolbar;

- (void)retainObject:(id)object;

@property (nonatomic, readonly, retain) UIView* toolbar;
@property (nonatomic, readonly, assign) CGFloat headerOffset;
@property (nonatomic, readonly, assign) BOOL autoCancelDisabled;
@property (nonatomic, readonly, assign) BOOL navigationBarHidden;
@property (nonatomic, readwrite, assign) BOOL disableReload;

@end
