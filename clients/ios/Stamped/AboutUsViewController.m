//
//  AboutUsViewController.m
//  Stamped
//
//  Created by Jake Zien on 11/2/11.
//  Copyright (c) 2011 Stamped. All rights reserved.
//

#import "AboutUsViewController.h"
#import "WebViewController.h"

@implementation AboutUsViewController

@synthesize scrollView = scrollView_;
@synthesize contentView = contentView_;
@synthesize versionLabel = versionLabel_;

#pragma mark - View lifecycle

- (void)dealloc {
  self.scrollView = nil;
  self.contentView = nil;
  self.versionLabel = nil;
  [super dealloc];
}

- (void)viewDidLoad {
  [super viewDidLoad];
  self.versionLabel.text =
      [NSString stringWithFormat:@"Version %@", [[NSBundle mainBundle] objectForInfoDictionaryKey:@"CFBundleShortVersionString"]];
  [self.scrollView addSubview:self.contentView];
  self.scrollView.contentSize = self.contentView.bounds.size;
}

- (void)viewDidUnload {
  [super viewDidUnload];
  self.versionLabel = nil;
  self.contentView = nil;
  self.scrollView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  [super viewWillAppear:animated];
  [self.navigationController setNavigationBarHidden:YES animated:animated];
}

- (void)viewWillDisappear:(BOOL)animated {
    [self.navigationController setNavigationBarHidden:NO animated:animated];
    [super viewWillDisappear:animated];
}

#pragma mark - Actions

- (IBAction)settingsButtonPressed:(id)sender {
  [self.navigationController popViewControllerAnimated:YES];
}

- (IBAction)followButtonPressed:(id)sender {
  NSURL* URL = [NSURL URLWithString:@"http://www.twitter.com/stampedapp/"];
  WebViewController* vc = [[WebViewController alloc] initWithURL:URL];
  [self.navigationController pushViewController:vc animated:YES];
  vc.navigationController.navigationBarHidden = NO;
  [vc release];
}

- (IBAction)stampedButtonPressed:(id)sender {
  NSURL* URL = [NSURL URLWithString:@"http://www.stamped.com/"];
  WebViewController* vc = [[WebViewController alloc] initWithURL:URL];
  [self.navigationController pushViewController:vc animated:YES];
  vc.navigationController.navigationBarHidden = NO;
  [vc release];
}

@end
