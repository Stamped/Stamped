//
//  STOAuthViewController.m
//  Stamped
//
//  Created by Jake Zien on 10/27/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "STOAuthViewController.h"
#import "STNavigationBar.h"

@implementation STOAuthViewController

@synthesize loadingIndicator = loadingIndicator_;
@synthesize reloadButton = reloadButton_;
@synthesize shareButton = shareButton_;

#pragma mark - View lifecycle

- (void)dealloc {
  self.loadingIndicator = nil;
  self.reloadButton = nil;
  self.shareButton = nil;
  [super dealloc];
}

- (void)viewWillAppear:(BOOL)animated {
  self.navigationController.navigationBarHidden = NO;
  STNavigationBar* navBar = (STNavigationBar*)self.navigationController.navigationBar;
  navBar.hideLogo = YES;
  [navBar setNeedsDisplay];
  [super viewWillAppear:animated];
}

- (void)viewDidLoad {
  ((STNavigationBar*)self.navigationController.navigationBar).hideLogo = YES;
  STNavigationBar* navBar = (STNavigationBar*)self.navigationController.navigationBar;
  navBar.hideLogo = YES;
  [navBar setNeedsDisplay];
  self.shareButton.hidden = YES;
  [super viewDidLoad];
}

- (void)viewDidUnload {
  self.loadingIndicator = nil;
  self.reloadButton = nil;
  self.shareButton = nil;
  [super viewDidUnload];
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
    return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

+ (NSString*)authNibName {
  return @"WebViewController";
}

- (void)webViewDidStartLoad:(UIWebView*)webView {
  [loadingIndicator_ startAnimating];
  reloadButton_.hidden = YES;
}

- (void)webViewDidFinishLoad:(UIWebView*)webView {
  [loadingIndicator_ stopAnimating];
  reloadButton_.hidden = NO;
  self.backButton.enabled = webView.canGoBack;
  self.forwardButton.enabled = webView.canGoForward;
}

- (void)webView:(UIWebView*)webView didFailLoadWithError:(NSError*)error {
  [self webViewDidFinishLoad:webView];
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Womp womp" 
                                                   message:error.localizedDescription
                                                  delegate:nil
                                         cancelButtonTitle:nil
                                         otherButtonTitles:@"OK", nil] autorelease];
  [alert show];
}

@end
