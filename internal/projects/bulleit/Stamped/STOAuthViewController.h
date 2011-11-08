//
//  STOAuthViewController.h
//  Stamped
//
//  Created by Jake Zien on 10/27/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "GTMOAuthViewControllerTouch.h"

@interface STOAuthViewController : GTMOAuthViewControllerTouch

@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingIndicator;
@property (nonatomic, retain) IBOutlet UIButton* reloadButton;
@property (nonatomic, retain) IBOutlet UIButton* shareButton;
@property (nonatomic, retain) IBOutlet UIView* toolbar;

@end
