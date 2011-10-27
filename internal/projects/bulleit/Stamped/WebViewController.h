//
//  WebViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface WebViewController : UIViewController <UIWebViewDelegate, UIActionSheetDelegate>

- (id)initWithURL:(NSURL*)url;

- (IBAction)shareButtonPressed:(id)sender;

@property (nonatomic, retain) IBOutlet UIWebView* webView;
@property (nonatomic, retain) IBOutlet UIActivityIndicatorView* loadingIndicator;
@property (nonatomic, retain) IBOutlet UIButton* backButton;
@property (nonatomic, retain) IBOutlet UIButton* forwardButton;
@property (nonatomic, retain) IBOutlet UIButton* reloadButton;
@property (nonatomic, retain) IBOutlet UIButton* shareButton;

@property (nonatomic, retain) NSURL* url;
@end
