//
//  WebViewController.m
//  Stamped
//
//  Created by Andrew Bonventre on 10/27/11.
//  Copyright (c) 2011 Stamped, Inc. All rights reserved.
//

#import "WebViewController.h"

@implementation WebViewController

@synthesize webView = webView_;
@synthesize url = url_;
@synthesize loadingIndicator = loadingIndicator_;
@synthesize backButton = backButton_;
@synthesize forwardButton = forwardButton_;
@synthesize reloadButton = reloadButton_;
@synthesize shareButton = shareButton_;
@synthesize toolbar = toolbar_;
@synthesize hideToolbar = hideToolbar_;

- (id)initWithURL:(NSURL*)url {
  self = [self initWithNibName:NSStringFromClass([self class]) bundle:nil];
  if (self) {
    self.url = url;
  }
  return self;
}

- (void)dealloc {
  if ([webView_ respondsToSelector:@selector(scrollView)])
    webView_.scrollView.delegate = nil;
  self.webView.delegate = nil;
  self.webView = nil;
  self.url = nil;
  self.loadingIndicator = nil;
  self.backButton = nil;
  self.forwardButton = nil;
  self.reloadButton = nil;
  self.shareButton = nil;
  self.toolbar = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  if (navBarWasHidden)
    self.navigationController.navigationBarHidden = YES;
  [super viewWillDisappear:animated];
  
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
}

- (void)viewDidAppear:(BOOL)animated {
  [super viewDidAppear:animated];
  shareButton_.enabled = YES;
  self.navigationController.navigationBarHidden = NO;
  [webView_ loadRequest:[NSURLRequest requestWithURL:url_]];
}

- (void)viewDidLoad {
  if (self.navigationController.navigationBarHidden)
    navBarWasHidden = YES;
  else
    navBarWasHidden = NO;
  [super viewDidLoad];
  if ([webView_ respondsToSelector:@selector(scrollView)])
    webView_.scrollView.delegate = self;
  toolbar_.hidden = hideToolbar_;
  CGRect frame = webView_.frame;
  frame.size.height = toolbar_.hidden ? 412 : 371;
  webView_.frame = frame;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  if ([webView_ respondsToSelector:@selector(scrollView)])
    webView_.scrollView.delegate = nil;
  self.webView.delegate = nil;
  self.webView = nil;
  self.url = nil;
  self.loadingIndicator = nil;
  self.backButton = nil;
  self.forwardButton = nil;
  self.reloadButton = nil;
  self.shareButton = nil;
  self.toolbar = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

- (IBAction)shareButtonPressed:(id)sender {
  UIActionSheet* sheet = [[[UIActionSheet alloc] initWithTitle:webView_.request.URL.absoluteString
                                                      delegate:self
                                             cancelButtonTitle:@"Cancel"
                                        destructiveButtonTitle:nil
                                             otherButtonTitles:@"Open in Safari", @"Copy link", nil] autorelease];
  sheet.actionSheetStyle = UIActionSheetStyleBlackOpaque;
  [sheet showInView:self.view];
  return;
}

- (void)hideToolbar:(BOOL)shouldHide {
  if (shouldHide && self.toolbar.hidden == NO) {
    self.toolbar.hidden = YES;
    CGRect frame = self.webView.frame;
    frame.size.height += self.toolbar.frame.size.height;
    self.webView.frame = frame;
  }
  else if (self.toolbar.hidden == YES) {
    self.toolbar.hidden = NO;
    CGRect frame = self.webView.frame;
    frame.size.height -= self.toolbar.frame.size.height;
    self.webView.frame = frame;
  }
}

#pragma mark - UIActionSheetDelegate methods.

- (void)actionSheet:(UIActionSheet*)actionSheet didDismissWithButtonIndex:(NSInteger)buttonIndex {
  if (buttonIndex == 0) {
    [[UIApplication sharedApplication] openURL:webView_.request.URL];
  } else if (buttonIndex == 1) {
    [UIPasteboard generalPasteboard].URL = webView_.request.URL;
  }
}

#pragma mark - UIWebViewDelegate methods.

- (void)webViewDidStartLoad:(UIWebView*)webView {
  [loadingIndicator_ startAnimating];
  reloadButton_.hidden = YES;
}

- (void)webViewDidFinishLoad:(UIWebView*)webView {
  [loadingIndicator_ stopAnimating];
  reloadButton_.hidden = NO;
  backButton_.enabled = webView.canGoBack;
  forwardButton_.enabled = webView.canGoForward;
}

- (void)webView:(UIWebView*)webView didFailLoadWithError:(NSError*)error {
  [self webViewDidFinishLoad:webView];
  UIAlertView* alert = [[[UIAlertView alloc] initWithTitle:@"Womp womp"
                                                   message:@"There was a problem loading this page."
                                                  delegate:nil
                                         cancelButtonTitle:nil
                                         otherButtonTitles:@"OK", nil] autorelease];
  [alert show];
}

@end
