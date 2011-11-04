//
//  TOSViewController.m
//  Stamped
//
//  Created by Jake Zien on 11/3/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "TOSViewController.h"

@implementation TOSViewController

@synthesize webView = webView_;
@synthesize settingsButton = settingsButton_;
@synthesize doneButton = doneButton_;

- (id)initWithURL:(NSURL*)aURL {
  URL = aURL;
  return [self initWithNibName:@"TOSViewController" bundle:nil];
}

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}

- (void)didReceiveMemoryWarning
{
    // Releases the view if it doesn't have a superview.
    [super didReceiveMemoryWarning];
    
    // Release any cached data, images, etc that aren't in use.
}

#pragma mark - View lifecycle

- (void)viewDidLoad {
  self.view.clipsToBounds = YES;
  self.webView.scalesPageToFit = YES;
  [self.webView loadRequest:[NSURLRequest requestWithURL:URL]];
  [super viewDidLoad];
}

- (void)viewDidUnload
{
  self.webView = nil;
  self.settingsButton = nil;
  self.doneButton = nil;
  [super viewDidUnload];
}

- (IBAction)done:(id)sender {
  UIViewController* vc = nil;
  if ([self respondsToSelector:@selector(presentingViewController)])
    vc = [(id)self presentingViewController];
  else
    vc = self.parentViewController;
  
  [vc dismissModalViewControllerAnimated:YES];
}

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}


@end
