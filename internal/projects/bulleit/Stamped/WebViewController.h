//
//  WebViewController.h
//  Stamped
//
//  Created by Andrew Bonventre on 10/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import <UIKit/UIKit.h>

@interface WebViewController : UIViewController <UIWebViewDelegate>

- (id)initWithURL:(NSURL*)url;

@property (nonatomic, retain) IBOutlet UIWebView* webView;
@property (nonatomic, retain) UIActivityIndicatorView* loadingIndicator;
@property (nonatomic, retain) NSURL* url;
@end
