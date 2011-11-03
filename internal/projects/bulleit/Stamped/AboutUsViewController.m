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

@synthesize scrollView;
@synthesize contentView;

- (id)initWithNibName:(NSString *)nibNameOrNil bundle:(NSBundle *)nibBundleOrNil
{
    self = [super initWithNibName:nibNameOrNil bundle:nibBundleOrNil];
    if (self) {
        // Custom initialization
    }
    return self;
}


#pragma mark - View lifecycle

- (void)viewDidLoad
{
  [super viewDidLoad];
  [self.scrollView addSubview:self.contentView];
  self.scrollView.contentSize = self.contentView.bounds.size;
}

- (void)viewDidUnload
{
  [super viewDidUnload];
  self.contentView = nil;
  self.scrollView = nil;
}

- (void)viewWillAppear:(BOOL)animated {
  self.navigationController.navigationBarHidden = YES;
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
