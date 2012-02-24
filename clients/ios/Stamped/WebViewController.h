//
//  WebViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

#import "STViewController.h"

@interface WebViewController : STViewController <UIWebViewDelegate, UIActionSheetDelegate> {
 @private 
  BOOL navBarWasHidden;
}

- (id)initWithURL:(NSURL*)url;

- (IBAction)shareButtonPressed:(id)sender;
- (void)hideToolbar:(BOOL)shouldHide;

@property (nonatomic, retain) IBOutlet UIWebView* webView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingIndicator;
@property (nonatomic, retain) IBOutlet UIButton* backButton;
@property (nonatomic, retain) IBOutlet UIButton* forwardButton;
@property (nonatomic, retain) IBOutlet UIButton* reloadButton;
@property (nonatomic, retain) IBOutlet UIButton* shareButton;
@property (nonatomic, retain) IBOutlet UIView* toolbar;

@property (nonatomic, assign) BOOL hideToolbar;
@property (nonatomic, retain) NSURL* url;
@end
