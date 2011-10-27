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

- (id)initWithURL:(NSURL*)url {
  self = [self initWithNibName:@"WebViewController" bundle:nil];
  if (self) {
    self.url = url;
  }
  return self;
}

- (void)dealloc {
  self.webView = nil;
  self.url = nil;
  self.loadingIndicator = nil;
  [super dealloc];
}

#pragma mark - View lifecycle

- (void)viewWillDisappear:(BOOL)animated {
  [super viewWillDisappear:animated];
  
}

- (void)viewDidLoad {
  [super viewDidLoad];
  [webView_ loadRequest:[NSURLRequest requestWithURL:url_]];
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.webView = nil;
  self.url = nil;
  self.loadingIndicator = nil;
}

- (BOOL)shouldAutorotateToInterfaceOrientation:(UIInterfaceOrientation)interfaceOrientation {
  return (interfaceOrientation == UIInterfaceOrientationPortrait);
}

@end
